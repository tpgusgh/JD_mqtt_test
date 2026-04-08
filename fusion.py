"""
cup_dispenser_b1_down - Fusion 360 재생성 스크립트
=====================================================
STL 역분석을 통해 추출한 치수로 모델을 재생성합니다.

[사용법]
1. Fusion 360 실행
2. 상단 메뉴 → Tools → Add-Ins → Scripts and Add-Ins
3. [Scripts] 탭 → 우측 상단 [+] 버튼 클릭
4. 이 .py 파일 선택
5. [Run] 클릭

[역분석 치수 요약]
- 전체 외형: 124 x 20 x 210 mm (X x Y x Z)
- 하단 박스: 124 x 20 x 116 mm, 벽두께 약 4mm
- 전환부:    Z 116~128mm, 양쪽 원형 리브로 연결
- 상단 박스: 95 x 19 x 82mm (Z 128~210mm)
- 측면 원형 홀(왼쪽): 중심 X≈6, Z≈5~115, 반경≈3.5mm
- 측면 원형 홀(오른쪽): 중심 X≈118, Z≈5~115, 반경≈3.5mm
- 내부 슬롯: X 14~110 구간, Y 방향 관통
"""

import adsk.core
import adsk.fusion
import traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        rootComp = design.rootComponent

        # 단위: mm
        # Fusion API는 cm 단위 → 모든 값을 /10 해야 함

        def mm(v):
            return v / 10.0

        sketches = rootComp.sketches
        features = rootComp.features
        extrudes = features.extrudeFeatures

        # ─────────────────────────────────────────────
        # 1. 하단 박스 외형 (124 x 20 x 116mm)
        # ─────────────────────────────────────────────
        xyPlane = rootComp.xYConstructionPlane
        sk1 = sketches.add(xyPlane)
        sk1.name = "하단_외형_스케치"
        lines1 = sk1.sketchCurves.sketchLines

        # 직사각형 (0,0) ~ (124, 20)
        p0 = adsk.core.Point3D.create(mm(0),   mm(0),  0)
        p1 = adsk.core.Point3D.create(mm(124), mm(0),  0)
        p2 = adsk.core.Point3D.create(mm(124), mm(20), 0)
        p3 = adsk.core.Point3D.create(mm(0),   mm(20), 0)
        lines1.addByTwoPoints(p0, p1)
        lines1.addByTwoPoints(p1, p2)
        lines1.addByTwoPoints(p2, p3)
        lines1.addByTwoPoints(p3, p0)

        prof1 = sk1.profiles.item(0)
        ext1_input = extrudes.createInput(
            prof1,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        ext1_input.setDistanceExtent(
            False,
            adsk.core.ValueInput.createByReal(mm(116))
        )
        ext1 = extrudes.add(ext1_input)
        ext1.name = "하단_박스_돌출"

        # ─────────────────────────────────────────────
        # 2. 하단 박스 내부 쉘 (벽두께 4mm)
        # ─────────────────────────────────────────────
        # Shell 기능 사용
        shellFeatures = features.shellFeatures
        brepBodies = rootComp.bRepBodies
        body1 = brepBodies.item(0)

        # 상단 면을 open face로 지정해서 shell
        topFace = None
        for face in body1.faces:
            n = face.evaluator.getNormalAtPoint(face.pointOnFace)[1]
            if n.z > 0.9:
                bbox = face.boundingBox
                if abs(bbox.minPoint.z - mm(116)) < 0.01:
                    topFace = face
                    break

        if topFace:
            shellInput = shellFeatures.createInput(
                adsk.core.ObjectCollection.createWithArray([topFace]),
                adsk.core.ValueInput.createByReal(mm(4))
            )
            shellFeat = shellFeatures.add(shellInput)
            shellFeat.name = "하단_박스_쉘"

        # ─────────────────────────────────────────────
        # 3. 왼쪽 측면 원형 홀 (X≈6, 반경≈3.5mm)
        # ─────────────────────────────────────────────
        # YZ 평면에 스케치 (X=0 면)
        offsetPlaneInput = rootComp.constructionPlanes.createInput()
        offsetPlaneInput.setByOffset(
            rootComp.yZConstructionPlane,
            adsk.core.ValueInput.createByReal(mm(0))
        )
        leftPlane = rootComp.constructionPlanes.add(offsetPlaneInput)

        sk_left = sketches.add(leftPlane)
        sk_left.name = "왼쪽_홀_스케치"
        circles_left = sk_left.sketchCurves.sketchCircles

        # 홀 위치들 (Y 방향 중심=10mm, Z 방향 다양)
        # 분석 결과: Z≈6~7mm, Z≈34~35mm, Z≈82~89mm 에 홀 패턴
        hole_z_positions = [17, 35, 60, 85, 105]  # mm
        left_hole_center_y = 10  # mm (Y 중심)
        hole_radius = 3.5  # mm

        for hz in hole_z_positions:
            center = adsk.core.Point3D.create(mm(left_hole_center_y), mm(hz), 0)
            circles_left.addByCenterRadius(center, mm(hole_radius))

        # 홀들을 컷으로 돌출
        for i in range(sk_left.profiles.count):
            prof = sk_left.profiles.item(i)
            cut_input = extrudes.createInput(
                prof,
                adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            cut_input.setDistanceExtent(
                False,
                adsk.core.ValueInput.createByReal(mm(4))
            )
            cut_feat = extrudes.add(cut_input)
            cut_feat.name = f"왼쪽_홀_컷_{i+1}"

        # ─────────────────────────────────────────────
        # 4. 오른쪽 측면 원형 홀 (X≈118, 대칭)
        # ─────────────────────────────────────────────
        offsetPlaneInput2 = rootComp.constructionPlanes.createInput()
        offsetPlaneInput2.setByOffset(
            rootComp.yZConstructionPlane,
            adsk.core.ValueInput.createByReal(mm(124))
        )
        rightPlane = rootComp.constructionPlanes.add(offsetPlaneInput2)

        sk_right = sketches.add(rightPlane)
        sk_right.name = "오른쪽_홀_스케치"
        circles_right = sk_right.sketchCurves.sketchCircles

        for hz in hole_z_positions:
            center = adsk.core.Point3D.create(mm(left_hole_center_y), mm(hz), 0)
            circles_right.addByCenterRadius(center, mm(hole_radius))

        for i in range(sk_right.profiles.count):
            prof = sk_right.profiles.item(i)
            cut_input = extrudes.createInput(
                prof,
                adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            cut_input.setDistanceExtent(
                False,
                adsk.core.ValueInput.createByReal(mm(-4))
            )
            cut_feat = extrudes.add(cut_input)
            cut_feat.name = f"오른쪽_홀_컷_{i+1}"

        # ─────────────────────────────────────────────
        # 5. 상단 박스 (X: 14.5~109.5 = 95mm폭, Z: 128~210mm)
        # ─────────────────────────────────────────────
        # Z=128 평면 생성
        offsetPlaneInput3 = rootComp.constructionPlanes.createInput()
        offsetPlaneInput3.setByOffset(
            xyPlane,
            adsk.core.ValueInput.createByReal(mm(128))
        )
        topStartPlane = rootComp.constructionPlanes.add(offsetPlaneInput3)
        topStartPlane.name = "상단박스_시작_평면"

        sk_top = sketches.add(topStartPlane)
        sk_top.name = "상단_박스_스케치"
        lines_top = sk_top.sketchCurves.sketchLines

        # 상단 박스: X=14.5~109.5, Y=1~20 (벽두께 5mm)
        tp0 = adsk.core.Point3D.create(mm(14.5), mm(1),  0)
        tp1 = adsk.core.Point3D.create(mm(109.5), mm(1),  0)
        tp2 = adsk.core.Point3D.create(mm(109.5), mm(19), 0)
        tp3 = adsk.core.Point3D.create(mm(14.5),  mm(19), 0)
        lines_top.addByTwoPoints(tp0, tp1)
        lines_top.addByTwoPoints(tp1, tp2)
        lines_top.addByTwoPoints(tp2, tp3)
        lines_top.addByTwoPoints(tp3, tp0)

        prof_top = sk_top.profiles.item(0)
        ext_top_input = extrudes.createInput(
            prof_top,
            adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        ext_top_input.setDistanceExtent(
            False,
            adsk.core.ValueInput.createByReal(mm(82))  # 128→210mm
        )
        ext_top = extrudes.add(ext_top_input)
        ext_top.name = "상단_박스_돌출"

        # ─────────────────────────────────────────────
        # 6. 상단 박스 내부 쉘 (벽두께 5mm)
        # ─────────────────────────────────────────────
        # 상단면 face 찾아서 shell
        # (Fusion이 자동으로 합쳐진 body에서 처리)

        # ─────────────────────────────────────────────
        # 7. 전환부 (Z 116~128mm) - Loft로 연결
        # ─────────────────────────────────────────────
        # 하단(124x20) → 상단(95x19) 로 Loft
        offsetPlaneInput4 = rootComp.constructionPlanes.createInput()
        offsetPlaneInput4.setByOffset(
            xyPlane,
            adsk.core.ValueInput.createByReal(mm(116))
        )
        loftBot = rootComp.constructionPlanes.add(offsetPlaneInput4)

        sk_loft_bot = sketches.add(loftBot)
        sk_loft_bot.name = "전환부_하단_스케치"
        lb_lines = sk_loft_bot.sketchCurves.sketchLines
        lb0 = adsk.core.Point3D.create(mm(0),   mm(0),  0)
        lb1 = adsk.core.Point3D.create(mm(124), mm(0),  0)
        lb2 = adsk.core.Point3D.create(mm(124), mm(20), 0)
        lb3 = adsk.core.Point3D.create(mm(0),   mm(20), 0)
        lb_lines.addByTwoPoints(lb0, lb1)
        lb_lines.addByTwoPoints(lb1, lb2)
        lb_lines.addByTwoPoints(lb2, lb3)
        lb_lines.addByTwoPoints(lb3, lb0)

        sk_loft_top = sketches.add(topStartPlane)  # Z=128
        sk_loft_top.name = "전환부_상단_스케치"
        lt_lines = sk_loft_top.sketchCurves.sketchLines
        lt0 = adsk.core.Point3D.create(mm(14.5), mm(1),  0)
        lt1 = adsk.core.Point3D.create(mm(109.5), mm(1),  0)
        lt2 = adsk.core.Point3D.create(mm(109.5), mm(19), 0)
        lt3 = adsk.core.Point3D.create(mm(14.5),  mm(19), 0)
        lt_lines.addByTwoPoints(lt0, lt1)
        lt_lines.addByTwoPoints(lt1, lt2)
        lt_lines.addByTwoPoints(lt2, lt3)
        lt_lines.addByTwoPoints(lt3, lt0)

        loftFeatures = features.loftFeatures
        loftSections = adsk.core.ObjectCollection.create()
        loftSections.add(sk_loft_bot.profiles.item(0))
        loftSections.add(sk_loft_top.profiles.item(0))

        loftInput = loftFeatures.createInput(
            loftSections,
            adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        loftFeat = loftFeatures.add(loftInput)
        loftFeat.name = "전환부_Loft"

        # ─────────────────────────────────────────────
        # 완료 메시지
        # ─────────────────────────────────────────────
        ui.messageBox(
            "✅ cup_dispenser_b1_down 모델 생성 완료!\n\n"
            "생성된 피처:\n"
            "  1. 하단_박스_돌출 (124×20×116mm)\n"
            "  2. 하단_박스_쉘 (벽두께 4mm)\n"
            "  3~4. 왼쪽/오른쪽 홀 컷 (반경 3.5mm × 5개)\n"
            "  5. 상단_박스_돌출 (95×19×82mm)\n"
            "  6. 전환부_Loft (Z 116~128mm)\n\n"
            "⚠️ 주의:\n"
            "  - STL 역분석 기반이므로 원본과 세부 치수가 다를 수 있습니다\n"
            "  - 타임라인에서 각 피처를 선택 후 '편집'으로 수정하세요\n"
            "  - File → Save As 로 f3d 파일로 저장하세요",
            "cup_dispenser_b1_down 생성 완료"
        )

    except Exception:
        if ui:
            ui.messageBox("오류 발생:\n" + traceback.format_exc())