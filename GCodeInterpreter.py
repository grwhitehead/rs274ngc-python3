import sys
import math
import numpy as np
from enum import Enum

from antlr4 import *
from GCodeLexer import GCodeLexer
from GCodeParser import GCodeParser
from GCodeVisitor import GCodeVisitor
from GCodeFormatter import GCodeFormatter
from GCodeParamMemory import GCodeParamMemory
from GCodeExprEvaluator import GCodeExprEvaluator


class GCodeAxis(Enum):
    X = 0,
    Y = 1,
    Z = 2,
    A = 3,
    B = 4,
    C = 5

class GCodePlane(Enum):
    XY = 0,
    YZ = 1,
    XZ = 2

class GCodeLengthUnits(Enum):
    INCHES = 0,
    MM = 1

class GCodeDistanceMode(Enum):
    ABSOLUTE = 0,
    INCREMENTAL = 1

class GCodeFeedRateMode(Enum):
    UNITS_PER_MINUTE = 0,
    INVERSE = 1

class GCodePathControlMode(Enum):
    EXACT_PATH = 0,
    EXACT_STOP = 1,
    CONTINUOUS = 2

class GCodeMotionMode(Enum):
    NONE = -1,
    RAPID = 0,
    LINEAR = 1,
    ARC_CW = 2,
    ARC_CCW = 3


class GCodeInterpreter(GCodeVisitor):
    
    def onMove(self, pos):
        pass
    
    def __init__(self):
        GCodeVisitor.__init__(self)
        
        self.verbose = False
        
        # parameters in machine units (INCHES)
        self.paramMemory = GCodeParamMemory()
        self.rapidRate = 200
        self.epsilon = 0.0001
        self.maxArcErr = 0.001
        
        # current position in absolute machine coordinates
        self.currentPos = np.zeros(6)
        
        # track min/max position, distance traveled, time in machine units
        self.minPos = np.full(6, sys.float_info.max)
        self.maxPos = np.full(6, -sys.float_info.max)
        self.dist = 0
        self.time = 0
        
        # program distances are transformed into machine units
        self.programLengthUnits = GCodeLengthUnits.INCHES
        self.programLengthUnitsConversion = 1.0
        
        # program coordinates are transformed into machine coordinates
        self.programDistanceMode = GCodeDistanceMode.ABSOLUTE
        self.programOffset = np.zeros(6)
        self.selectedCoordinateSystem = int(self.paramMemory.getValue(5220))
        self.programOrigin = self.paramMemory.getVector(5201+20*self.selectedCoordinateSystem, 6)
        
        self.selectedPlane = GCodePlane.XY
        self.feedRateMode = GCodeFeedRateMode.UNITS_PER_MINUTE
        self.feedRate = 0
        self.spindleSpeed = 0
        self.selectedTool = 0
        self.tool = 0
        self.pathControlMode = GCodePathControlMode.EXACT_PATH
        self.motionMode = GCodeMotionMode.LINEAR
    
    #
    # command processing
    #
    
    def visitProgram(self, ctx:GCodeParser.ProgramContext):
        # visit each line, stopping if program ends early (see shouldVisitNextChild)
        self.endProgram = False
        self.visitChildren(ctx)
    
    def shouldVisitNextChild(self, node, currentResult):
        if isinstance(node, GCodeParser.ProgramContext):
            return not self.endProgram
        return True
    
    def visitLine(self, ctx:GCodeParser.LineContext):
        if self.verbose:
            print(GCodeFormatter().visit(ctx), file=sys.stderr, end="")
        
        ev = GCodeExprEvaluator(self.paramMemory)
        
        # process comments
        #for s in ctx.segment():
        #    c = s.comment()
        #    if c:
        #        pass
        
        # process commands
        cl = []
        al = []
        self.cmdGroups = 0
        self.axisWordsPresent = False
        self.axisWordsUsed = False
        self.moveInAbsoluteCoordinates = False
        for s in ctx.segment():
            w = s.mid_line_word()
            if w:
                w_l = w.mid_line_letter()
                w_v = ev.visit(w.real_value())
                if self.verbose:
                    print("{} {:.4f}".format(w_l.getText(), w_v), file=sys.stderr)
                if _isCmd((w_l,w_v)):
                    if not _isCmdSupported((w_l,w_v)):
                        raise Exception("not supported {}".format(w.getText()))
                    w_g = _cmdGroup((w_l,w_v))
                    if w_g > 0:
                        if self.cmdGroups & 1<<w_g:
                            raise Exception("modal group conflict")
                        else:
                            self.cmdGroups |= 1<<w_g
                    cl.append((w_l,w_v))
                else:
                    if _isAxis((w_l,w_v)):
                        self.axisWordsPresent = True
                    al.append((w_l,w_v))
        cl.sort(key=_cmdOrder)
        for w in cl:
            _cmdHandler(w)(self, w[1], al)
        if self.axisWordsPresent and not self.axisWordsUsed:
            if self.motionMode == GCodeMotionMode.NONE:
                raise Exception("axis words not allowed")
            self.handleMotion(al)
        if self.endProgram:
            self.handleEnd()
        
        # process parameter settings
        for s in ctx.segment():
            p = s.parameter_setting()
            if p:
                p_i = int(ev.visit(p.parameter_index().real_value()))
                p_v = ev.visit(p.real_value())
                self.paramMemory.setValue(p_i, p_v)
    
    def handleF(self, v, args): # set feed rate
        self.feedRate = v/self.programLengthUnitsConversion
    def handleS(self, v, args): # set spindle speed
        self.spindleSpeed = v
    def handleT(self, v, args): # select tool
        self.selectedTool = v
    
    def handleG0(self, v, args): # rapid motion (X Y Z A B C)
        self.motionMode = GCodeMotionMode.RAPID
        self.handleMotion(args)
    def handleG1(self, v, args): # linear motion (X Y Z A B C)
        self.motionMode = GCodeMotionMode.LINEAR
        self.handleMotion(args)
    def handleG2(self, v, args): # cw arc (X Y Z A B C I J K R)
        self.motionMode = GCodeMotionMode.ARC_CW
        self.handleMotion(args)
    def handleG3(self, v, args): # ccw arc (X Y Z A B C I J K R)
        self.motionMode = GCodeMotionMode.ARC_CCW
        self.handleMotion(args)
    def handleG4(self, v, args): # dwell (P seconds)
        p = 0
        for (w_l,w_v) in args:
            if w_l.P():
                p = w_v
        self.time += p
    
    def handleG10(self, v, args): # set coordinate system data
        l = 0
        p = 0
        for (w_l,w_v) in args:
            if w_l.L():
                l = int(w_v)
            elif w_l.P():
                p = int(w_v)
                if p < 1 or p > 9:
                    raise Exception("unknown coordinate system {}".format(p))
        origin = self.paramMemory.getVector(5201+20*p, 6)
        for (w_l,w_v) in args:
            if w_l.X():
                origin[0] = w_v/self.programLengthUnitsConversion
            elif w_l.Y():
                origin[1] = w_v/self.programLengthUnitsConversion
            elif w_l.Z():
                origin[2] = w_v/self.programLengthUnitsConversion
            elif w_l.A():
                origin[3] = w_v
            elif w_l.B():
                origin[4] = w_v
            elif w_l.C():
                origin[5] = w_v
        self.paramMemory.setVector(5201+20*p, 6, origin)
        if self.selectedCoordinateSystem == p:
            self.programOrigin = origin
        self.axisWordsUsed = True
    
    def handleG17(self, v, args): # set xy plane
        self.selectedPlane = GCodePlane.XY
    def handleG18(self, v, args): # set xz plane
        self.selectedPlane = GCodePlane.YZ
    def handleG19(self, v, args): # set yz plane
        self.selectedPlane = GCodePlane.XZ
    
    def handleG20(self, v, args): # in units
        self.programLengthUnits = GCodeLengthUnits.INCHES
        self.programLengthUnitsConversion = 1.0
    def handleG21(self, v, args): # mm units
        self.programLengthUnits = GCodeLengthUnits.MM
        self.programLengthUnitsConversion = 25.4
    
    def handleG28(self, v, args): # return home (5161-5166), by way of X Y Z A B C
        self.handleMoveHome(self.paramMemory.getVector(5161, 6), args)
    def handleG30(self, v, args): # return home (5181-5186), by way of X Y Z A B C
        self.handleMoveHome(self.paramMemory.getVector(5181, 6), args)
    
    def handleG53(self, v, args): # move in absolute coordinates
        self.moveInAbsoluteCoordinates = True
    
    def handleG54(self, v, args): # coordinate system 1 (5221-5226)
        self.selectedCoordinateSystem = 1
        self.programOrigin = self.paramMemory.getVector(5221, 6)
    def handleG55(self, v, args): # coordinate system 2 (5241-5246)
        self.selectedCoordinateSystem = 2
        self.programOrigin = self.paramMemory.getVector(5241, 6)
    def handleG56(self, v, args): # coordinate system 3 (5261-5266)
        self.selectedCoordinateSystem = 3
        self.programOrigin = self.paramMemory.getVector(5261, 6)
    def handleG57(self, v, args): # coordinate system 4 (5281-5286)
        self.selectedCoordinateSystem = 4
        self.programOrigin = self.paramMemory.getVector(5281, 6)
    def handleG58(self, v, args): # coordinate system 5 (5301-5306)
        self.selectedCoordinateSystem = 5
        self.programOrigin = self.paramMemory.getVector(5301, 6)
    def handleG59(self, v, args): # coordinate system 6 (5321-5326)
        self.selectedCoordinateSystem = 6
        self.programOrigin = self.paramMemory.getVector(5321, 6)
    def handleG59_1(self, v, args): # coordinate system 7 (5341-5346)
        self.selectedCoordinateSystem = 7
        self.programOrigin = self.paramMemory.getVector(5341, 6)
    def handleG59_2(self, v, args): # coordinate system 8 (5361-5366)
        self.selectedCoordinateSystem = 8
        self.programOrigin = self.paramMemory.getVector(5361, 6)
    def handleG59_3(self, v, args): # coordinate system 9 (5381-5386)
        self.selectedCoordinateSystem = 9
        self.programOrigin = self.paramMemory.getVector(5381, 6)
    
    def handleG61(self, v, args): # exact path mode
        self.pathControlMode = GCodePathControlMode.EXACT_PATH
    def handleG61_1(self, v, args): # exact stop mode
        self.pathControlMode = GCodePathControlMode.EXACT_STOP
    def handleG64(self, v, args): # continuous mode
        self.pathControlMode = GCodePathControlMode.CONTINUOUS
    
    def handleG80(self, v, args): # stop motion
        self.motionMode = GCodeMotionMode.NONE
    
    def handleG90(self, v, args): # absolute distance mode
        self.programDistanceMode = GCodeDistanceMode.ABSOLUTE
    def handleG91(self, v, args): # inceremental distance mode
        self.programDistanceMode = GCodeDistanceMode.INCREMENTAL
    
    def handleG92(self, v, args): # set coordinate system offset and store in memory (5211-5216)
        for (w_l,w_v) in args:
            if w_l.X():
                self.programOffset[0] = self.currentPos[0]-self.programOrigin[0]-w_v/self.programLengthUnitsConversion
            elif w_l.Y():
                self.programOffset[1] = self.currentPos[1]-self.programOrigin[1]-w_v/self.programLengthUnitsConversion
            elif w_l.Z():
                self.programOffset[2] = self.currentPos[2]-self.programOrigin[2]-w_v/self.programLengthUnitsConversion
            elif w_l.A():
                self.programOffset[3] = self.currentPos[3]-self.programOrigin[3]-w_v
            elif w_l.B():
                self.programOffset[4] = self.currentPos[4]-self.programOrigin[4]-w_v
            elif w_l.C():
                self.programOffset[5] = self.currentPos[5]-self.programOrigin[5]-w_v
        self.paramMemory.setVector(5211, 6, self.programOffset)
        self.axisWordsUsed = True
    def handleG92_1(self, v, args): # cancel coordinate system offset and clear memory (5211-5216)
        self.programOffset = np.zeros(6)
        self.paramMemory.setVector(5211, 6, self.programOffset)
    def handleG92_2(self, v, args): # cancel coordinate system offset
        self.programOffset = np.zeros(6)
    def handleG92_3(self, v, args): # load coordinate system offset from memory (5211-5216)
        self.programOffset = self.paramMemory.getVector(5211, 6)
    
    #def handleG93(self, v, args): # inverse feed rate mode
    #    self.feedRateMode = GCodeFeedRateMode.INVERSE
    def handleG94(self, v, args): # units per minute feed rate mode
        self.feedRateMode = GCodeFeedRateMode.UNITS_PER_MINUTE
    
    def handleM0(self, v, args): # program stop
        pass
    def handleM1(self, v, args): # optional program stop
        pass
    def handleM60(self, v, args): # program stop, pallet shuttle
        pass
    
    def handleM2(self, v, args): # program end
        self.endProgram = True
    def handleM30(self, v, args): # program end, pallet shuttle
        self.endProgram = True
    
    def handleM3(self, v, args): # spindle on cw
        pass
    def handleM4(self, v, args): # spindle on ccw
        pass
    def handleM5(self, v, args): # stop spindle
        pass
    
    def handleM6(self, v, args): # change tool
        self.tool = self.selectedTool
    
    def handleM7(self, v, args): # mist coolant on
        pass
    def handleM8(self, v, args): # flood coolant on
        pass
    def handleM9(self, v, args): # stop coolant
        pass
    
    def handleM48(self, v, args): # enable speed and feed overrides
        pass
    def handleM49(self, v, args): # disable speed and feed overrides
        pass
    
    def handleMotion(self, args):
        if not self.axisWordsPresent:
            raise Exception("axis words missing")
        if self.axisWordsUsed:
            raise Exception("axis words already used")
        targetPos = np.copy(self.currentPos)
        ijk = [0,0,0]
        r = 0
        for (w_l,w_v) in args:
            if w_l.X():
                if self.moveInAbsoluteCoordinates:
                    targetPos[0] = w_v/self.programLengthUnitsConversion
                elif self.programDistanceMode == GCodeDistanceMode.ABSOLUTE:
                    targetPos[0] = self.programOffset[0]+self.programOrigin[0]+w_v/self.programLengthUnitsConversion
                else:
                    targetPos[0] += w_v/self.programLengthUnitsConversion
            elif w_l.Y():
                if self.moveInAbsoluteCoordinates:
                    targetPos[1] = w_v/self.programLengthUnitsConversion
                elif self.programDistanceMode == GCodeDistanceMode.ABSOLUTE:
                    targetPos[1] = self.programOffset[1]+self.programOrigin[1]+w_v/self.programLengthUnitsConversion
                else:
                    targetPos[1] += w_v/self.programLengthUnitsConversion
            elif w_l.Z():
                if self.moveInAbsoluteCoordinates:
                    targetPos[2] = w_v/self.programLengthUnitsConversion
                elif self.programDistanceMode == GCodeDistanceMode.ABSOLUTE:
                    targetPos[2] = self.programOffset[2]+self.programOrigin[2]+w_v/self.programLengthUnitsConversion
                else:
                    targetPos[2] += w_v/self.programLengthUnitsConversion
            elif w_l.A():
                if self.moveInAbsoluteCoordinates:
                    targetPos[3] = w_v
                elif self.programDistanceMode == GCodeDistanceMode.ABSOLUTE:
                    targetPos[3] = self.programOffset[3]+self.programOrigin[3]+w_v
                else:
                    targetPos[3] += w_v
            elif w_l.B():
                if self.moveInAbsoluteCoordinates:
                    targetPos[4] = w_v
                elif self.programDistanceMode == GCodeDistanceMode.ABSOLUTE:
                    targetPos[4] = self.programOffset[4]+self.programOrigin[4]+w_v
                else:
                    targetPos[4] += w_v
            elif w_l.C():
                if self.moveInAbsoluteCoordinates:
                    targetPos[5] = w_v
                elif self.programDistanceMode == GCodeDistanceMode.ABSOLUTE:
                    targetPos[5] = self.programOffset[5]+self.programOrigin[5]+w_v
                else:
                    targetPos[5] += w_v
            elif w_l.I():
                ijk[0] = w_v/self.programLengthUnitsConversion
            elif w_l.J():
                ijk[1] = w_v/self.programLengthUnitsConversion
            elif w_l.K():
                ijk[2] = w_v/self.programLengthUnitsConversion
            elif w_l.R():
                r = w_v/self.programLengthUnitsConversion
        if self.motionMode == GCodeMotionMode.RAPID:
            self.doMove(targetPos, self.rapidRate)
            self.axisWordsUsed = True
        elif self.motionMode == GCodeMotionMode.LINEAR:
            self.doMove(targetPos, self.feedRate)
            self.axisWordsUsed = True
        elif self.motionMode == GCodeMotionMode.ARC_CW or self.motionMode == GCodeMotionMode.ARC_CCW:
            if self.selectedPlane == GCodePlane.XY:
                px = 0
                py = 1
                pz = 2
            elif self.selectedPlane == GCodePlane.YZ:
                px = 2
                py = 0
                pz = 1
            elif self.selectedPlane == GCodePlane.XZ:
                px = 1
                py = 2
                pz = 0
            x0 = self.currentPos[px]
            y0 = self.currentPos[py]
            x1 = targetPos[px]
            y1 = targetPos[py]
            if abs(r) > 0:
                p0 = np.array([x0,y0])
                p1 = np.array([x1,y1])
                pm = (p0+p1)/2
                v = pm-p0
                vd = math.hypot(v[0],v[1])
                if vd < self.epsilon or not vd-abs(r) < self.epsilon:
                    raise Exception("arc radius error")
                uv = v/vd
                uvp = np.array([-uv[1],uv[0]])*np.sign(r)
                if self.motionMode == GCodeMotionMode.ARC_CCW:
                    uvp *= -1
                c = pm-uvp
                c = pm-uvp*math.sqrt(r*r-vd*vd)
                c_x = c[0]
                c_y = c[1]
                r = abs(r)
            elif math.hypot(ijk[px],ijk[py]) > 0:
                c_x = x0+ijk[px]
                c_y = y0+ijk[py]
                r = math.hypot(x0-c_x,y0-c_y)
                r1 = math.hypot(x1-c_x,y1-c_y)
                if abs(r-r1) > 2*self.epsilon:
                    raise Exception("arc radius error")
            else:
                raise Exception("arc radius error")
            a0 = math.atan2(x0-c_x,y0-c_y)
            a1 = math.atan2(x1-c_x,y1-c_y)
            a = (a1-a0)
            if a < 0:
                a += 2*math.pi
            if self.motionMode == GCodeMotionMode.ARC_CCW:
                a = 2*math.pi - a
            if a < self.epsilon:
                a = 2*math.pi
            # approximate arc with straight line segments
            # the midpoint of each line segment must be within maxArcErr of the arc radius
            maxastep = 2*math.acos((r-self.maxArcErr)/r)
            nsteps = math.ceil(a/maxastep)
            astep = a/nsteps
            zstep = (targetPos[pz]-self.currentPos[pz])/nsteps
            for i in range(nsteps):
                ai = astep*i
                if self.motionMode == GCodeMotionMode.ARC_CCW:
                    ai = 2*math.pi-ai
                aPos = np.copy(self.currentPos)
                aPos[px] = c_x + r*math.sin(a0+ai)
                aPos[py] = c_y + r*math.cos(a0+ai)
                aPos[pz] += zstep
                self.doMove(aPos, self.feedRate)
            self.doMove(targetPos, self.feedRate)
            self.axisWordsUsed = True
    
    def handleMoveHome(self, homePos, args):
        if len(args) > 0:
            targetPos = np.copy(self.currentPos)
            for (w_l,w_v) in args:
                if w_l.X():
                    if self.programDistanceMode == GCodeDistanceMode.ABSOLUTE:
                        targetPos[0] = self.programOffset[0]+self.programOrigin[0]+w_v/self.programLengthUnitsConversion
                    else:
                        targetPos[0] += w_v/self.programLengthUnitsConversion
                elif w_l.Y():
                    if self.programDistanceMode == GCodeDistanceMode.ABSOLUTE:
                        targetPos[1] = self.programOffset[1]+self.programOrigin[1]+w_v/self.programLengthUnitsConversion
                    else:
                        targetPos[1] += w_v/self.programLengthUnitsConversion
                elif w_l.Z():
                    if self.programDistanceMode == GCodeDistanceMode.ABSOLUTE:
                        targetPos[2] = self.programOffset[2]+self.programOrigin[2]+w_v/self.programLengthUnitsConversion
                    else:
                        targetPos[2] += w_v/self.programLengthUnitsConversion
                elif w_l.A():
                    if self.programDistanceMode == GCodeDistanceMode.ABSOLUTE:
                        targetPos[3] = self.programOffset[3]+self.programOrigin[3]+w_v
                    else:
                        targetPos[3] += w_v
                elif w_l.B():
                    if self.programDistanceMode == GCodeDistanceMode.ABSOLUTE:
                        targetPos[4] = self.programOffset[4]+self.programOrigin[4]+w_v
                    else:
                        targetPos[4] += w_v
                elif w_l.C():
                    if self.programDistanceMode == GCodeDistanceMode.ABSOLUTE:
                        targetPos[5] = self.programOffset[5]+self.programOrigin[5]+w_v
                    else:
                        targetPos[5] += w_v
            self.doMove(targetPos, self.rapidRate)
        self.doMove(homePos, self.rapidRate)
        self.axisWordsUsed = True
    
    def handleEnd(self):
        self.selectedCoordinateSystem = int(self.paramMemory.getValue(5220))
        self.programOrigin = self.paramMemory.getVector(5201+20*self.selectedCoordinateSystem, 6)
        self.programOffset = np.zeros(6)
        self.selectedPlane = GCodePlane.XY
        self.programDistanceMode = GCodeDistanceMode.ABSOLUTE
        self.feedRateMode = GCodeFeedRateMode.UNITS_PER_MINUTE
        self.motionMode = GCodeMotionMode.LINEAR
    
    def doMove(self, targetPos, targetRate):
        if targetRate > 0:
            p0 = self.currentPos
            p1 = targetPos
            dist = math.hypot(p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2])
            if not dist < self.epsilon:
                self.onMove(p1)
                self.minPos = np.minimum(self.minPos,p1)
                self.maxPos = np.maximum(self.maxPos,p1)
                self.dist += dist
                self.time += dist/targetRate
                self.currentPos = targetPos

#
# command processing lookup tables
#

# See 3.4 Modal Groups
#
# group 0 = {G4, G10, G28, G30, G53, G92, G92.1, G92.2, G92.3} non-modal
#
# group 1 = {G0, G1, G2, G3, G38.2, G80, G81, G82, G83, G84, G85, G86, G87, G88, G89} motion
# group 2 = {G17, G18, G19} plane selection
# group 3 = {G90, G91} distance mode
# group 5 = {G93, G94} feed rate mode
# group 6 = {G20, G21} units
# group 7 = {G40, G41, G42} cutter radius compensation
# group 8 = {G43, G49} tool length offset
# group 10 = {G98, G99} return mode in canned cycles
# group 12 = {G54, G55, G56, G57, G58, G59, G59.1, G59.2, G59.3} coordinate system selection
# group 13 = {G61, G61.1, G64} path control mode
#
# group 4 = {M0, M1, M2, M30, M60} stopping
# group 6 = {M6} tool change
# group 7 = {M3, M4, M5} spindle turning
# group 8 = {M7, M8, M9} coolant (special case: M7 and M8 may be active at the same time)
# group 9 = {M48, M49} enable/disable feed and speed override switches

# See 3.8 Order of Execution
#
# 1. comment (includes message).
# 2. set feed rate mode (G93, G94 — inverse time or per minute).
# 3. set feed rate (F).
# 4. set spindle speed (S).
# 5. select tool (T).
# 6. change tool (M6).
# 7. spindle on or off (M3, M4, M5).
# 8. coolant on or off (M7, M8, M9).
# 9. enable or disable overrides (M48, M49).
# 10. dwell (G4).
# 11. set active plane (G17, G18, G19).
# 12. set length units (G20, G21).
# 13. cutter radius compensation on or off (G40, G41, G42)
# 14. cutter length compensation on or off (G43, G49)
# 15. coordinate system selection (G54, G55, G56, G57, G58, G59, G59.1, G59.2, G59.3).
# 16. set path control mode (G61, G61.1, G64)
# 17. set distance mode (G90, G91).
# 18. set retract mode (G98, G99).
# 19. home (G28, G30) or
#     change coordinate system data (G10) or
#     set axis offsets (G92, G92.1, G92.2, G94).
# 20. perform motion (G0 to G3, G80 to G89), as modified (possibly) by G53.
# 21. stop (M0, M1, M2, M30, M60).

_cmdDict = {
    GCodeParser.G: {
        #
        # 2. set feed rate mode (G93, G94 — inverse time or per minute).
        #
        #'93.0': (5, 2, GCodeInterpreter.handleG93),
        '94.0': (5, 2, GCodeInterpreter.handleG94),
        #
        # 10. dwell (G4).
        #
        '4.0': (0, 10, GCodeInterpreter.handleG4),
        #
        # 11. set active plane (G17, G18, G19).
        #
        '17.0': (2, 11, GCodeInterpreter.handleG17),
        '18.0': (2, 11, GCodeInterpreter.handleG18),
        '19.0': (2, 11, GCodeInterpreter.handleG19),
        #
        # 12. set length units (G20, G21).
        #
        '20.0': (6, 12, GCodeInterpreter.handleG20),
        '21.0': (6, 12, GCodeInterpreter.handleG21),
        #
        # 13. cutter radius compensation on or off (G40, G41, G42)
        #
        #'40.0': (7, 13, GCodeInterpreter.handleG40),
        #'41.0': (7, 13, GCodeInterpreter.handleG41),
        #'42.0': (7, 13, GCodeInterpreter.handleG42),
        #
        # 14. cutter length compensation on or off (G43, G49)
        #
        #'43.0': (8, 14, GCodeInterpreter.handleG43),
        #'49.0': (8, 14, GCodeInterpreter.handleG49),
        #
        # 15. coordinate system selection (G54, G55, G56, G57, G58, G59, G59.1, G59.2, G59.3).
        #
        '54.0': (12, 15, GCodeInterpreter.handleG54),
        '55.0': (12, 15, GCodeInterpreter.handleG55),
        '56.0': (12, 15, GCodeInterpreter.handleG56),
        '57.0': (12, 15, GCodeInterpreter.handleG57),
        '58.0': (12, 15, GCodeInterpreter.handleG58),
        '59.0': (12, 15, GCodeInterpreter.handleG59),
        '59.1': (12, 15, GCodeInterpreter.handleG59_1),
        '59.2': (12, 15, GCodeInterpreter.handleG59_2),
        '59.3': (12, 15, GCodeInterpreter.handleG59_3),
        #
        # 16. set path control mode (G61, G61.1, G64)
        #
        '61.0': (13, 16, GCodeInterpreter.handleG61),
        '61.1': (13, 16, GCodeInterpreter.handleG61_1),
        '64.0': (13, 16, GCodeInterpreter.handleG64),
        #
        # 17. set distance mode (G90, G91).
        #
        "53.0": (0, 17, GCodeInterpreter.handleG53),
        '90.0': (3, 17, GCodeInterpreter.handleG90),
        '91.0': (3, 17, GCodeInterpreter.handleG91),
        #
        # 18. set retract mode (G98, G99).
        #
        #'98.0': (10, 18, GCodeInterpreter.handleG98),
        #'99.0': (10, 18, GCodeInterpreter.handleG99),
        #
        # 19. change coordinate system data (G10) or
        #     home (G28, G30) or
        #     set axis offsets (G92, G92.1, G92.2, G92.3).
        #
        '10.0': (0, 19, GCodeInterpreter.handleG10),
        '28.0': (0, 19, GCodeInterpreter.handleG28),
        '30.0': (0, 19, GCodeInterpreter.handleG30),
        '92.0': (0, 19, GCodeInterpreter.handleG92),
        '92.1': (0, 19, GCodeInterpreter.handleG92_1),
        '92.2': (0, 19, GCodeInterpreter.handleG92_2),
        '92.3': (0, 19, GCodeInterpreter.handleG92_3),
        #
        # 20. perform motion (G0 to G3, G80 to G89), as modified (possibly) by G53.
        #
        '0.0': (1, 20, GCodeInterpreter.handleG0),
        '1.0': (1, 20, GCodeInterpreter.handleG1),
        '2.0': (1, 20, GCodeInterpreter.handleG2),
        '3.0': (1, 20, GCodeInterpreter.handleG3),
        #'38.2': (1, 20, GCodeInterpreter.handleG38_2),
        '80.0': (1, 20, GCodeInterpreter.handleG80),
        #'81.0': (1, 20, GCodeInterpreter.handleG81),
        #'82.0': (1, 20, GCodeInterpreter.handleG82),
        #'83.0': (1, 20, GCodeInterpreter.handleG83),
        #'84.0': (1, 20, GCodeInterpreter.handleG84),
        #'85.0': (1, 20, GCodeInterpreter.handleG85),
        #'86.0': (1, 20, GCodeInterpreter.handleG86),
        #'87.0': (1, 20, GCodeInterpreter.handleG87),
        #'88.0': (1, 20, GCodeInterpreter.handleG88),
        #'89.0': (1, 20, GCodeInterpreter.handleG89)
    },
    GCodeParser.M: {
        #
        # 6. change tool (M6).
        #
        '6.0': (6, 6, GCodeInterpreter.handleM6),
        #
        # 7. spindle on or off (M3, M4, M5).
        #
        '3.0': (7, 7, GCodeInterpreter.handleM3),
        '4.0': (7, 7, GCodeInterpreter.handleM4),
        '5.0': (7, 7, GCodeInterpreter.handleM5),
        #
        # 8. coolant on or off (M7, M8, M9).
        #
        '7.0': (8, 8, GCodeInterpreter.handleM7),
        '8.0': (8, 8, GCodeInterpreter.handleM8),
        '9.0': (8, 8, GCodeInterpreter.handleM9),
        #
        # 9. enable or disable overrides (M48, M49).
        #
        '48.0': (9, 9, GCodeInterpreter.handleM48),
        '49.0': (9, 9, GCodeInterpreter.handleM49),
        #
        # 21. stop (M0, M1, M2, M30, M60).
        #
        '0.0': (4, 21, GCodeInterpreter.handleM0),
        '1.0': (4, 21, GCodeInterpreter.handleM1),
        '2.0': (4, 21, GCodeInterpreter.handleM2),
        '30.0': (4, 21, GCodeInterpreter.handleM30),
        '60.0': (4, 21, GCodeInterpreter.handleM60)
    },
    #
    # 3. set feed rate (F).
    #
    GCodeParser.F: (0, 3, GCodeInterpreter.handleF),
    #
    # 4. set spindle speed (S).
    #
    GCodeParser.S: (0, 4, GCodeInterpreter.handleS),
    #
    # 5. select tool (T).
    #
    GCodeParser.T: (0, 5, GCodeInterpreter.handleT)
}

def _isCmd(w):
    (w_l,w_v) = w
    k = w_l.start.type
    return k in _cmdDict

def _isCmdSupported(w):
    return _cmdEntry(w) is not None

def _cmdGroup(w):
    return _cmdEntry(w)[0]

def _cmdOrder(w):
    return _cmdEntry(w)[1]

def _cmdHandler(w):
    return _cmdEntry(w)[2]

def _cmdEntry(w):
    (w_l,w_v) = w
    k = w_l.start.type
    if not k in _cmdDict:
        return None
    e = _cmdDict[k]
    if type(e) is dict:
        k2 = "{:.1f}".format(w_v)
        if not k2 in e:
            return None
        e = e[k2]
    return e

_axisDict = {
    GCodeParser.X: GCodeAxis.X,
    GCodeParser.Y: GCodeAxis.Y,
    GCodeParser.Z: GCodeAxis.Z,
    GCodeParser.A: GCodeAxis.A,
    GCodeParser.B: GCodeAxis.B,
    GCodeParser.C: GCodeAxis.C
}

def _isAxis(w):
    (w_l,w_v) = w
    k = w_l.start.type
    return k in _axisDict

def _axisEntry(w):
    (w_l,w_v) = w
    k = w_l.start.type
    if not k in _axisDict:
        return None
    return _axisDict[k]
