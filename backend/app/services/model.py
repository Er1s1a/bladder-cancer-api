"""
AI 模型推理服务 — EORTC 膀胱癌复发/进展风险评估

基于 EORTC 风险量表 (Sylvester et al., European Urology, 2006).
适用于非肌层浸润性膀胱癌 (NMIBC: Ta, T1) 患者经 TURBT 术后
的复发和进展风险预测.

参考文献:
  Sylvester RJ, van der Meijden APM, Oosterlinck W, et al.
  Predicting recurrence and progression in individual patients with
  stage Ta T1 bladder cancer using EORTC risk tables.
  Eur Urol. 2006;49(3):466-477.
"""

import math


def predict_risk(
    dicom_link: str = "",
    lesion_size: float = 0,
    lesion_count: int = 0,
    tumor_grade: str = "",
    invasion_depth: str = "",
    lymph_node_metastasis: str = "",
    prior_recurrence: str = "primary",
    concomitant_cis: bool = False
) -> dict:
    """
    EORTC 膀胱癌复发/进展风险预测.

    输入参数:
        lesion_size:          最大病灶直径 (mm)
        lesion_count:         病灶数量
        tumor_grade:          肿瘤分级 G1/G2/G3 (WHO 1973)
        invasion_depth:       T分期 Ta/T1/T2/T3/T4
        lymph_node_metastasis: N分期 N0/N1/N2/N3
        prior_recurrence:     既往复发情况 "primary" / "≤1 per year" / "＞1 per year"
        concomitant_cis:      是否合并原位癌 (CIS)

    返回:
        recurrence_risk:         5年复发概率 (%)
        disease_probability:     5年疾病进展概率 (%)
        risk_level:              综合风险等级 low/medium/high
        clinical_data:           临床参数 + EORTC评分明细
        heatmap_data:            模拟膀胱热力图
        heatmap_interpretation:  文字解读
        recommendations:         随访建议
    """

    # ============================
    # 1. EORTC 复发评分 (0-17+)
    # ============================
    recurrence_score = 0
    recurrence_details = []

    # 病灶数量
    if lesion_count == 1:
        recurrence_score += 0
        recurrence_details.append(f"单发 (+0)")
    elif 2 <= lesion_count <= 7:
        recurrence_score += 3
        recurrence_details.append(f"多发2-7个 (+3)")
    elif lesion_count >= 8:
        recurrence_score += 6
        recurrence_details.append(f"多发≥8个 (+6)")

    # 病灶大小 (mm -> cm)
    size_cm = lesion_size / 10.0 if lesion_size > 0 else 0
    if size_cm < 3:
        recurrence_score += 0
        recurrence_details.append(f"病灶<3cm (+0)")
    else:
        recurrence_score += 3
        recurrence_details.append(f"病灶≥3cm (+3)")

    # 既往复发率
    pr = prior_recurrence.strip() if prior_recurrence else "primary"
    if pr == "primary" or pr == "":
        recurrence_score += 0
        recurrence_details.append("初发 (+0)")
    elif pr in ("≤1 per year", "≤1/year", "≤1/yr"):
        recurrence_score += 2
        recurrence_details.append("复发≤1次/年 (+2)")
    elif pr in ("＞1 per year", ">1/year", "＞1/yr", ">1 per year", "> 1 per year"):
        recurrence_score += 4
        recurrence_details.append("复发>1次/年 (+4)")

    # T分期
    if invasion_depth == "Ta":
        recurrence_score += 0
        recurrence_details.append("Ta (+0)")
    elif invasion_depth == "T1":
        recurrence_score += 1
        recurrence_details.append("T1 (+1)")
    elif invasion_depth in ("T2", "T3", "T4"):
        recurrence_score += 3
        recurrence_details.append(f"{invasion_depth}肌层浸润 (+3)")

    # 合并CIS
    if concomitant_cis:
        recurrence_score += 1
        recurrence_details.append("合并CIS (+1)")
    else:
        recurrence_details.append("无CIS (+0)")

    # 分级
    if tumor_grade == "G1":
        recurrence_score += 0
        recurrence_details.append("G1 (+0)")
    elif tumor_grade == "G2":
        recurrence_score += 1
        recurrence_details.append("G2 (+1)")
    elif tumor_grade == "G3":
        recurrence_score += 2
        recurrence_details.append("G3 (+2)")

    # 淋巴结阳性 (EORTC之外, 但临床意义重大)
    if lymph_node_metastasis in ("N1", "N2", "N3"):
        recurrence_score += 4
        recurrence_details.append(f"{lymph_node_metastasis}淋巴结阳性 (+4)")

    # ============================
    # 2. EORTC 进展评分 (0-23+)
    # ============================
    progression_score = 0
    progression_details = []

    # 病灶数量
    if lesion_count == 1:
        progression_score += 0
        progression_details.append("单发 (+0)")
    else:
        progression_score += 3
        progression_details.append("多发 (+3)")

    # 病灶大小
    if size_cm < 3:
        progression_score += 0
        progression_details.append("病灶<3cm (+0)")
    else:
        progression_score += 3
        progression_details.append("病灶≥3cm (+3)")

    # 既往复发率
    if pr in ("primary", ""):
        progression_score += 0
        progression_details.append("初发 (+0)")
    else:
        progression_score += 2
        progression_details.append("有复发史 (+2)")

    # T分期 (进展的核心因子)
    if invasion_depth == "Ta":
        progression_score += 0
        progression_details.append("Ta (+0)")
    elif invasion_depth == "T1":
        progression_score += 4
        progression_details.append("T1 (+4)")
    elif invasion_depth in ("T2", "T3", "T4"):
        progression_score += 8
        progression_details.append(f"{invasion_depth}肌层浸润 (+8)")

    # 合并CIS (强进展因子)
    if concomitant_cis:
        progression_score += 6
        progression_details.append("合并CIS (+6)")
    else:
        progression_details.append("无CIS (+0)")

    # 分级 (强进展因子)
    if tumor_grade in ("G1", "G2"):
        progression_score += 0
        progression_details.append(f"{tumor_grade} (+0)")
    elif tumor_grade == "G3":
        progression_score += 5
        progression_details.append("G3 (+5)")

    # 淋巴结阳性
    if lymph_node_metastasis in ("N1", "N2", "N3"):
        progression_score += 6
        progression_details.append(f"{lymph_node_metastasis}淋巴结阳性 (+6)")

    # ============================
    # 3. 查表获取 1年/5年 概率
    # ============================

    # — 复发概率 —
    if recurrence_score == 0:
        recurrence_1yr, recurrence_5yr = 15.0, 31.0
        re_category = "低危"
    elif 1 <= recurrence_score <= 4:
        recurrence_1yr, recurrence_5yr = 24.0, 46.0
        re_category = "中低危"
    elif 5 <= recurrence_score <= 9:
        recurrence_1yr, recurrence_5yr = 38.0, 62.0
        re_category = "中高危"
    else:
        base = recurrence_score
        if base <= 17:
            recurrence_1yr, recurrence_5yr = 61.0, 78.0
            re_category = "高危"
        else:
            recurrence_1yr = min(100, 61 + (base - 17) * 4)
            recurrence_5yr = min(100, 78 + (base - 17) * 3)
            re_category = "极高危"

    # — 进展概率 —
    if progression_score == 0:
        progression_1yr, progression_5yr = 0.2, 0.8
        pg_category = "低危"
    elif 2 <= progression_score <= 6:
        progression_1yr, progression_5yr = 1.0, 6.0
        pg_category = "中危"
    elif 7 <= progression_score <= 13:
        progression_1yr, progression_5yr = 5.0, 17.0
        pg_category = "高危"
    else:
        base = progression_score
        if base <= 23:
            progression_1yr, progression_5yr = 17.0, 45.0
            pg_category = "极高危"
        else:
            progression_1yr = min(100, 17 + (base - 23) * 6)
            progression_5yr = min(100, 45 + (base - 23) * 5)
            pg_category = "极高危"

    # ============================
    # 4. 综合风险等级
    # ============================
    # 以进展概率为核心 (进展比复发更具临床意义)
    if progression_5yr >= 17:
        risk_level = "high"
    elif progression_5yr >= 6:
        risk_level = "medium"
    else:
        risk_level = "low"

    # T2+ 或 N+ 强制至少 medium
    if invasion_depth in ("T2", "T3", "T4") or lymph_node_metastasis in ("N1", "N2", "N3"):
        if risk_level == "low":
            risk_level = "medium"

    # ============================
    # 5. 热力图数据
    # ============================
    hotspots = _generate_hotspots(lesion_count, risk_level)

    # ============================
    # 6. 文字解读
    # ============================
    interpretation = _generate_interpretation(
        recurrence_score, recurrence_1yr, recurrence_5yr, re_category,
        progression_score, progression_1yr, progression_5yr, pg_category,
        risk_level, tumor_grade, invasion_depth,
        lymph_node_metastasis, lesion_count, concomitant_cis
    )

    # ============================
    # 7. 随访建议
    # ============================
    recommendations = _generate_recommendations(
        risk_level, recurrence_score, progression_score,
        tumor_grade, invasion_depth
    )

    return {
        "recurrence_risk": round(recurrence_5yr, 1),
        "disease_probability": round(progression_5yr, 1),
        "risk_level": risk_level,
        "clinical_data": {
            "tumorGrade": tumor_grade,
            "invasionDepth": invasion_depth,
            "lymphNodeMetastasis": lymph_node_metastasis,
            "lesionSize": lesion_size,
            "lesionCount": lesion_count,
            "priorRecurrence": pr,
            "concomitantCis": concomitant_cis,
            "eorcRecurrenceScore": recurrence_score,
            "eorcRecurrenceCategory": re_category,
            "eorcProgressionScore": progression_score,
            "eorcProgressionCategory": pg_category,
            "recurrence1yr": round(recurrence_1yr, 1),
            "recurrence5yr": round(recurrence_5yr, 1),
            "progression1yr": round(progression_1yr, 1),
            "progression5yr": round(progression_5yr, 1),
        },
        "heatmap_data": {"hotspots": hotspots},
        "heatmap_interpretation": interpretation,
        "recommendations": recommendations,
        "model_version": "EORTC-v1.0"
    }


# ============================================================
# 辅助函数
# ============================================================

def _generate_hotspots(lesion_count: int, risk_level: str) -> list[dict]:
    """根据病灶数量和风险等级生成模拟热力点."""
    count = max(0, lesion_count)

    # 按照 膀胱解剖分区 预设点位 (顶/后/左/右/颈/三角区)
    anatomic_positions = [
        (0.50, 0.15, "膀胱顶部"),
        (0.50, 0.45, "膀胱后壁"),
        (0.25, 0.60, "膀胱左侧壁"),
        (0.75, 0.60, "膀胱右侧壁"),
        (0.50, 0.85, "三角区"),
        (0.50, 0.95, "膀胱颈"),
        (0.35, 0.30, "左后壁"),
        (0.65, 0.30, "右后壁"),
    ]

    # 颜色和强度按风险等级
    hi_color = "#C95A4A"  # 红
    md_color = "#C8803A"  # 橙
    lo_color = "#3D8B6E"  # 绿

    hotspots = []
    used_positions = set()

    max_spots = min(count, len(anatomic_positions))
    max_spots = max(max_spots, 1) if count > 0 else max_spots

    for i in range(max_spots):
        x, y, label = anatomic_positions[i % len(anatomic_positions)]

        # 前面的病灶为高风险, 后面的逐步降低
        if i < max(1, max_spots // 3):
            color = hi_color
            intensity = 0.85 + i * 0.05
            risk_tag = "高风险病灶"
        elif i < max(1, max_spots * 2 // 3):
            color = md_color
            intensity = 0.60 + i * 0.03
            risk_tag = "中风险区域"
        else:
            color = lo_color
            intensity = 0.35 + i * 0.03
            risk_tag = "低风险区域"

        hotspots.append({
            "x": round(x, 2),
            "y": round(y, 2),
            "radius": round(0.18 - i * 0.02, 2),
            "color": color,
            "intensity": round(min(1.0, intensity), 2),
            "label": f"{risk_tag} ({label})"
        })
        used_positions.add(i % len(anatomic_positions))

    # 如果没有病灶, 返回空白
    if not hotspots:
        return []

    return hotspots


def _generate_interpretation(
    recurrence_score, recurrence_1yr, recurrence_5yr, re_category,
    progression_score, progression_1yr, progression_5yr, pg_category,
    risk_level, tumor_grade, invasion_depth,
    lymph_node_metastasis, lesion_count, concomitant_cis
) -> str:
    """生成中文解读报告（结构化文本，前端按节解析）."""

    risk_cn = {"high": "高", "medium": "中等", "low": "低"}
    risk_narratives = {
        "high": "综合 EORTC 评分结果，您处于高风险等级。请务必与主治医生保持紧密沟通，按时完成各项复查。",
        "medium": "综合 EORTC 评分结果，您处于中等风险等级。保持规律随访是控制病情的关键，请遵医嘱安排复查计划。",
        "low": "综合 EORTC 评分结果，您处于低风险等级。预后良好，但仍需按医嘱完成基础随访计划，不可掉以轻心。"
    }
    narrative = risk_narratives.get(risk_level, risk_narratives["medium"])

    cis_text = "合并 CIS" if concomitant_cis else "未合并 CIS"
    lymph_text = lymph_node_metastasis if lymph_node_metastasis else "N0"

    lines = [
        f"【复发风险】您的 EORTC 复发评分为 {recurrence_score} 分，属于{re_category}。5 年复发概率约 {recurrence_5yr}%，1 年复发概率约 {recurrence_1yr}%。",
        f"【进展风险】您的 EORTC 进展评分为 {progression_score} 分，属于{pg_category}。5 年进展概率约 {progression_5yr}%，1 年进展概率约 {progression_1yr}%。",
        f"【临床特征】{tumor_grade or '未知'} 级肿瘤，{invasion_depth or '未知'} 期浸润，{lymph_text} 淋巴结，共 {lesion_count} 个病灶，{cis_text}。",
        f"【综合评估】您处于{risk_cn.get(risk_level, risk_level)}风险等级。{narrative}"
    ]
    return "\n".join(lines)


def _generate_recommendations(
    risk_level: str,
    recurrence_score: int,
    progression_score: int,
    tumor_grade: str,
    invasion_depth: str
) -> list[str]:
    """根据风险等级生成随访建议（仅作参考，非诊疗方案）."""

    recommendations = []

    if progression_score >= 14:
        recommendations = [
            "您的综合风险评分较高，建议尽快与泌尿外科主治医生预约沟通",
            "定期随访对于监测病情变化至关重要，请按医生要求的频次复查",
            "关注尿液性状及排尿习惯变化，如有异常及时就医",
        ]
    elif 7 <= progression_score <= 13:
        recommendations = [
            "您处于中等偏高复发风险区间，建议保持规律随访",
            "请与主治医生讨论适合您个体情况的监测计划",
            "注意记录每次检查结果，便于长期追踪分析",
        ]
    elif 2 <= progression_score <= 6:
        recommendations = [
            "您的风险处于可控范围，按时随访是保持健康的关键",
            "请遵医嘱安排常规复查，不要因感觉良好而跳过检查",
        ]
    else:
        recommendations = [
            "您的评估结果显示风险较低，预后相对良好",
            "请按医嘱完成基础随访计划，保持良好生活习惯",
        ]

    if invasion_depth in ("T2", "T3", "T4"):
        recommendations.append("当前评估提示病变浸润较深，建议尽快前往泌尿外科门诊咨询")

    recommendations.extend([
        "戒烟 — 吸烟是膀胱癌最重要的可控危险因素",
        "多饮水 — 每日 2000mL 以上，避免憋尿",
        "避免接触芳香胺类化学致癌物",
        "本报告仅作参考，具体诊疗方案请以临床医生判断为准",
    ])

    return recommendations
