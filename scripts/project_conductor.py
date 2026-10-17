#!/usr/bin/env python3
"""Owner-facing deterministic draft conductor. This is NOT an AI, price oracle,
GitHub worker, visual renderer or approval engine. No calls, tokens or installs.
User answers must stay OUTSIDE this public source repository.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from portfolio_intake import assess, questionnaire, IntakeError

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "config/senior-gates.json"
FLAGS = {
    "accounts": "accounts", "persistence": "persistence",
    "live_media": "media", "payments": "payments",
    "real_sensitive_data": "sensitive", "physical_control": "physical",
}
BUDGET_PARTS = ("static_host", "backend", "database", "email", "bandwidth",
                "storage", "backups", "monitoring", "domain", "support")
INTERVIEW_VERSION = "1.0"


def safe_output(target):
    """Avoid accidentally publishing owner-specific answers to the source tree."""
    target = Path(target).expanduser().resolve()
    if target == ROOT or ROOT in target.parents:
        raise IntakeError("Save owner files OUTSIDE this public GitHub repository")
    if target.exists() or target.is_symlink():
        raise IntakeError("Output exists: refusing to overwrite private owner data")
    if len(str(target)) > 2000:
        raise IntakeError("Output location too long")
    return target


def write_new(target, payload):
    dest = safe_output(target)
    dest.parent.mkdir(parents=True, exist_ok=True)
    # exclusive open avoids a check/write race and avoids silent clobbers
    with dest.open("x", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")
    return dest


def read_private(path):
    file = Path(path)
    if file.is_symlink() or file.stat().st_size > 300_000:
        raise IntakeError("Missing, symlinked or oversized private owner input")
    result = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise IntakeError("Private intake must be a JSON object")
    return result


def try_amount(raw):
    # For a noncoder shorthand Q08: "0 IQD", "40 USD". Unknown is NOT zero.
    if not isinstance(raw, str):
        return None
    found = re.fullmatch(r"\s*(\d{1,9}(?:[.,]\d{1,2})?)\s*([A-Za-z]{3})\s*(?:شهريا|بالشهر|monthly|مرة واحدة)?\s*", raw.strip(), re.I)
    if not found:
        return None
    return {"amount": float(found.group(1).replace(",", ".")),
            "currency": found.group(2).upper()}


def try_load(raw):
    # Range "100-300" is not one observation; requiring an explicit numeric
    # estimate is safer than silently picking a midpoint.
    if not isinstance(raw, str):
        return None
    found = re.fullmatch(r"\s*(\d{1,9})\s*", raw.strip())
    return int(found.group(1)) if found else None


def interactive(project_id, output, stream_in=input, stream_out=print):
    if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9._-]{1,63}", project_id):
        raise IntakeError("project-id should be a short Latin slug (example: watched)")
    stream_out("مقابلة أولية: 20 سؤالًا. لا تحتاج خبرة برمجية. اكتب «ما اعرف» إن لم تعرف.")
    stream_out("للأرقام اكتب عددًا فقط في سؤالَي 6 و7؛ والميزانية مثل: 0 IQD أو 0 USD.")
    answers = {}
    for item in questionnaire():
        answers[item["id"]] = stream_in(item["prompt"] + "\n> ").strip() or "unknown"
    monthly, one_time = try_amount(answers["Q08"]), try_amount(answers["Q09"])
    expectation = {}
    for name, key in (("monthly_users", "Q06"), ("peak_concurrent", "Q07")):
        value = try_load(answers[key])
        if value is not None:
            expectation[name] = value
    # No regex may authorize payments/medical/media/robotic capabilities.
    doc = {"project_id": project_id, "kind": "undecided",
           "release_mode": "private_preview",
           "monthly_budget": monthly, "one_time_budget": one_time,
           "expected": expectation,
           "answers": answers, "risk_flags": {
               "real_sensitive_data": None, "live_media": None,
               "payments": None, "physical_control": None},
           "capabilities": {"accounts": None, "persistence": None},
           "cost_components": list(BUDGET_PARTS), "provider_quotes": [],
           "reference_repositories": [],
           "target_repo": None,
           "interview_version": INTERVIEW_VERSION,
           "note": "Unconfirmed fields remain unknown. Private preview is a safety default, not a claim that owner approved launch."}
    target = write_new(output, doc)
    stream_out("حُفظت الإجابات محليًا خارج المستودع: " + str(target))
    stream_out("الخطوة التالية: راجع التصنيفات والمبالغ مع الشات قبل إنتاج أي خطة تنفيذ.")
    return doc


def classify(doc):
    explicit = doc.get("capabilities", {})
    if not isinstance(explicit, dict):
        raise IntakeError("capabilities must be an object, never guessed")
    flags = doc.get("risk_flags", {})
    if not isinstance(flags, dict):
        raise IntakeError("risk_flags must be an object")
    answers = doc.get("answers", {})
    values = {
        "accounts": explicit.get("accounts"),
        "persistence": explicit.get("persistence"),
        "media": flags.get("live_media"),
        "payments": flags.get("payments"),
        "sensitive": flags.get("real_sensitive_data"),
        "physical": flags.get("physical_control")}
    for key, val in values.items():
        if val is not None and type(val) is not bool:
            raise IntakeError("Capability must be true, false or null: " + key)
    return values


def architecture_options(signals):
    # Give candidates, not fabricated quality/cost certification.
    accounts, persistence = signals["accounts"], signals["persistence"]
    if accounts is False and persistence is False:
        preferred = "STATIC_FIRST"
        rationale = "Confirmed: no accounts, no durable records; avoid paying for a backend."
    elif accounts is True or persistence is True:
        preferred = "REVIEW_MANAGED_BACKEND"
        rationale = "Accounts or cross-device stored data require a trusted boundary and backup plan; free plan not guaranteed."
    else:
        preferred = "UNDECIDED"
        rationale = "Account and persistence requirements have not been explicitly classified."
    return {
        "provisional_direction": preferred, "why": rationale,
        "candidates": [
            {"id": "static", "fit": "public info or browser-only disposable demo",
             "risk": "cannot honestly provide shared durable accounts, trusted permissions or paid orders"},
            {"id": "managed-backend", "fit": "small product needing auth and persistent data",
             "risk": "vendor quotas, email sending, backups, data protection and operational costs require quotes"},
            {"id": "self-hosted-monolith", "fit": "backend with controlled hosting and available operator",
             "risk": "someone must handle upgrades, recovery, security patches and monitoring"},
            {"id": "existing-service", "fit": "integrate existing event/video/content platform when it meets journeys",
             "risk": "license and provider terms, branding limits, lock-in and usage thresholds"}],
        "choice_approved": False}


def problem_probes(doc, signals):
    answers = doc.get("answers", {})
    if not isinstance(answers, dict):
        raise IntakeError("answers must be an object")
    probes = []
    if any(v is None for v in signals.values()):
        probes.append({"code": "CAPABILITY_CLASSIFICATION", "ask": "هل يحتاج حسابات وحفظ دائم أو بث/دفع/بيانات حساسة/أجهزة فعلية؟ أكد نعم أو لا لكل عنصر.", "blocks": "production design and dispatch"})
    if signals["media"] is True:
        probes.append({"code": "VIDEO_BUILD_OR_INTEGRATE", "ask": "كم مشاركًا متزامنًا وكم ساعة شهريًا؟ هل تقبل رابط منصة لقاءات جاهزة؟", "blocks": "self-hosted conferencing"})
    if signals["sensitive"] is True:
        probes.append({"code": "SENSITIVE_DATA", "ask": "من المسؤول عن الحذف والتصحيح والوصول والتبليغ والاحتفاظ؟ هل لديك مراجعة مختصة؟", "blocks": "live sensitive data"})
    if signals["payments"] is True:
        probes.append({"code": "PAYMENT_FLOW", "ask": "كيف يُثبت الدفع ويتعامل مع المكرر والمبالغ المرتجعة والنزاع؟", "blocks": "live payments"})
    if signals["physical"] is True:
        probes.append({"code": "DEVICE_SAFETY", "ask": "كيف يُوقف الجهاز إذا انقطع الاتصال ومن المخوّل بتحريكه؟", "blocks": "physical actuation"})
    budget = doc.get("monthly_budget")
    if isinstance(budget, dict) and budget.get("amount") == 0:
        probes.append({"code": "ZERO_BUDGET", "ask": "هل تقبل دومينًا فرعيًا وخدمة قد تتوقف عند الوصول للحد المجاني؟", "blocks": "any paid dependency"})
    if not doc.get("reference_repositories"):
        probes.append({"code": "GITHUB_EVIDENCE", "ask": "اجمع مشروعين أو ثلاثة يؤدي كل منها نفس رحلة المستخدم، ثم تحقق من ترخيص كل مشروع والنسخة والأصول والتكلفة.", "blocks": "source reuse, not independent learning"})
    return probes


def task_drafts(project_id, signals):
    """Milestones are *proposals* to be refined against actual repository files."""
    rows = [
        ("AUDIT", "فحص المستودع/المشروع الحالي وPR والروابط والصلاحيات وتحديد الموجود فعليًا",
         "تقرير يثبت كل وظيفة تعمل وما لا يعمل وروابط كود حقيقية",
         "راجع المستودع والنسخة والـCI؛ لا تكتب كودًا جديدًا", []),
        ("JOURNEY", "خريطة التجربة الأساسية وحالات الانتظار/الفشل والصفحات الحقيقية",
         "صف رحلة قابلة للاختبار مع دور المستخدم والمدير",
         "راجع تدفق الشاشة والأزرار وجميع حالات الشبكة", ["AUDIT"]),
        ("REUSE", "بحث 2-3 بدائل GitHub ومنتج جاهز مع تراخيص ونسخ مثبتة",
         "جدول REUSE/INTEGRATE/LEARN/REBUILD مع سبب وفحوص أصول",
         "قارِن commit والرخصة والوظائف والتكلفة بلا نسخ شيفرة غير مرخصة", ["AUDIT"]),
        ("COST", "احسب الاستضافة عادي/ذروة/تعافي بالدومين والبريد والتخزين والإرسال والمراقبة",
         "ثلاثة سيناريوهات واضحة؛ أي بند بلا سعر موسوم غير مسعّر",
         "تحقق من روابط الأسعار وتاريخها وحجم الاستخدام وسقف الميزانية", ["JOURNEY"]),
        ("ADR", "حدّد هيكلًا صغيرًا وبديلًا ومخاطر التزامن والحذف والبيانات",
         "سجل قرار معماري وفروض وأسباب واختبار رفض للبديل",
         "راجع مع الفريق منطق الحدود والصلاحيات والاسترجاع", ["REUSE","COST"]),
        ("DESIGN", "صمّم صفحات وتفاعلًا مميزًا مناسبًا للجمهور ودعم العربي والهاتف",
         "خريطة صفحات ونموذج بصري معلّم CONCEPT لا يُدعى أنه شاشة منجزة",
         "راجع وصول لوحة المفاتيح وتباين الألوان وأعباء الصور/الخطوط", ["JOURNEY","ADR"]),
        ("SLICE", "نفّذ رحلة المستخدم الرئيسية كاملة من الزر إلى التأكيد الحقيقي",
         "إجراء يتغيّر على الخادم أو يشرح أنه محلي، ويصمد بعد إعادة التحميل",
         "اختبار متصفح حقيقي للنجاح والفشل والتحقق من البيانات", ["DESIGN"]),
    ]
    last = "SLICE"
    if signals["accounts"] is not False or signals["sensitive"] is True:
        rows.append(("AUTH", "منع الوصول لبيانات غير المالك عند الاتصال المباشر بالـAPI",
                    "كل صفقة وصلاحية محمية داخل الخادم وليست واجهة فقط",
                    "اختبار مستخدمين منفصلين وطلبات IDOR وصلاحية المدير", ["ADR","SLICE"]))
        last="AUTH"
    if signals["persistence"] is not False:
        rows.append(("DATA", "تحقق من الكتابة المتزامنة واستعادة السجلات ونسخة احتياطية فعلية",
                    "لا توجد عمليات مكررة أو فقد صامت في التعارض أو عطل الشبكة",
                    "اختبار تعديلين متزامنين واستعادة نسخة بعد حذف تجريبي", [last]))
        last="DATA"
    rows.extend([
        ("NEGATIVE", "راجع الفشل الأمني والأجهزة البطيئة وRTL والتكلفة الفعلية",
         "دليل إخفاق متعمد وإصلاح أو حظر لكل خطر حرج",
         "اختبارات browser/API/RTL/p95 بالمحاكاة حسب النطاق المحدد", [last]),
        ("REVIEW", "اطلب أربع مراجعات مستقلة بأدلة وروابط وملفات SHA256",
         "لا تعلن جاهزية دون دليل وتوقيع منفصل لكل مراجعة",
         "شغّل بوابة packet ثم reconciler الخاصة بالمشرف بشكل read-only", ["NEGATIVE","COST"]),
    ])
    return [
      {"id":project_id+"-"+suffix,"objective":goal,"acceptance":accept,
       "verification":verify,"depends_on":[project_id+"-"+d for d in deps],
       "state":"DRAFT_NOT_AUTHORIZED", "human_review_required":True}
      for suffix,goal,accept,verify,deps in rows
    ]


def evaluate(doc):
    assessment = assess(doc)
    signals = classify(doc)
    probes = problem_probes(doc,signals)
    source_data = json.loads(GATES.read_text(encoding="utf-8"))
    selected = []
    for gate in source_data["gates"]:
        flag = gate["when"]
        applies = flag == "always" or signals.get(flag) is True
        unknown_flag = flag != "always" and signals.get(flag) is None
        if applies or unknown_flag:
            selected.append({**gate,"applicability": "CONDITIONAL_UNKNOWN" if unknown_flag else "APPLICABLE",
                             "status":"NOT_TESTED"})
    budget = assessment.get("estimate", {})
    blockers = list(assessment["blockers"])
    if any(x["applicability"] == "CONDITIONAL_UNKNOWN" for x in selected):
        blockers.append({"code":"UNCLASSIFIED_TRUST_BOUNDARY",
                         "reason":"Review the unknown capabilities before implementation"})
    if not doc.get("reference_repositories"):
        blockers.append({"code":"RESEARCH_NOT_DONE","reason":"No verified reference apps have been compared"})
    if assessment["estimate"]["monthly_quoted_subtotal"] is None:
        blockers.append({"code":"COST_NOT_QUOTED","reason":"$0 estimated would be fictional"})
    can_plan = assessment["status"] == "READY_FOR_PLANNING"
    return {"schema_version":"1.0", "project_id":doc["project_id"],
      "assessment_status":assessment["status"], "planning_discussion_allowed":can_plan,
      "owner_safe_summary":{
         "goal":str(doc.get("answers",{}).get("Q02",""))[:600],
         "primary_journey":str(doc.get("answers",{}).get("Q04",""))[:600],
         "expected":doc.get("expected",{}),
         "budget":doc.get("monthly_budget"),
         "quoted_total":budget.get("monthly_quoted_subtotal"),
         "unpriced":budget.get("unpriced_components"),
         "confidence":"Proposal only: no live site, verified pricing, approved design or secure deployment claimed."},
      "architecture":architecture_options(signals),
      "question_followups":probes,
      "conditional_gates":selected,
      "reference_repositories":[{"url":r.get("url"),"reuse":"STUDY_ONLY" if not (r.get("license_checked") and r.get("version_checked")) else "MANUAL_REVIEW_REQUIRED"}
                               for r in doc.get("reference_repositories",[])],
      "visual_concept_brief":{"label":"CONCEPT / NOT A SCREENSHOT",
         "pages_to_sketch":["أول شاشة للزائر","العمل الأساسي وماذا يحدث بعد ضغط الزر","شاشة إدارة المحتوى عند الحاجة","حالات فارغة وبطيئة وفشل"],
         "principles":["ابدأ بالمحتوى والرحلة وليس اللون", "مراعاة الهاتف واللغة العربية عند الحاجة", "لا صور زخرفية غير متصلة بوظيفة", "صورة مفهوم لا دليل على أن المنتج يعمل"],
         "image_generated":False},
      "plan_draft":task_drafts(doc["project_id"],signals),
      "skeptical_findings":blockers,
      "reviewers_needed":["feasibility", "architecture", "security", "design"],
      "real_commit_verified":False, "real_browser_verified":False,
      "cost_independently_verified":False, "manager_packet_issued":False,
      "implementation_authorized":False, "merge_authorized":False,
      "deployment_authorized":False, "spending_authorized":False,
      "next_step":"Verify missing facts + independent reviews; feed manually refined plan to existing packet validator."}



def markdown_owner_report(report):
    """Readable private synopsis. Unknown stays unknown; never turns a plan into approval."""
    info = report["owner_safe_summary"]
    arch = report["architecture"]
    def display(value):
        if value is None:
            return "غير معروف / لم يُتحقق منه"
        if isinstance(value, dict):
            return ", ".join(f"{display(k)}: {display(v)}" for k, v in value.items())
        return str(value).replace("<", "&lt;").replace(">", "&gt;").replace("|", "/").replace("\n", " ").strip()[:500] or "غير معروف"
    lines = [
        "# تقرير مبدئي للمشروع: " + display(report["project_id"]),
        "",
        "هذا تحليل أولي للمراجعة، وليس تطبيقًا مبنيًا أو تصميمًا منفذًا أو تصريحًا بالنشر.",
        "",
        "## ما الذي نعرفه؟",
        "- الهدف: " + display(info["goal"]),
        "- أهم رحلة للمستخدم: " + display(info["primary_journey"]),
        "- عدد المستخدمين المتوقع: " + display(info["expected"]),
        "- الحد الشهري الذي وضعته: " + display(info["budget"]),
        "- مجموع الأسعار الموثقة: " + display(info["quoted_total"]),
        "- بنود تكلفتها غير محسومة: " + display(info["unpriced"]),
        "",
        "## القرار المعماري المؤقت",
        "- الاتجاه: " + display(arch["provisional_direction"]),
        "- السبب: " + display(arch["why"]),
        "- **لم تُعتمد أي هيكلية نهائيًا.** يجب مراجعة البدائل وحجم الاستخدام والصلاحيات.",
        "",
        "## أسئلة مهمة قبل كتابة الكود",
    ]
    probes = report["question_followups"]
    lines.extend("- " + display(x["ask"]) + " (يمنع: " + display(x["blocks"]) + ")" for x in probes)
    if not probes:
        lines.append("- لم يُولّد هذا الفحص سؤالًا إضافيًا؛ مراجعة الواقع ما زالت مطلوبة.")
    lines += ["", "## المخاطر والقرارات الناقصة"]
    findings = report["skeptical_findings"]
    lines.extend("- " + display(x.get("code", "?")) + ": " + display(x.get("reason", x.get("field", ""))) for x in findings)
    if not findings:
        lines.append("- لا توجد موانع آلية مكتشفة؛ هذا ليس إثباتًا لسلامة الموقع.")
    lines += ["", "## مهام مقترحة للمراجعة وليست قيد التنفيذ"]
    for task in report["plan_draft"]:
        lines.append("- " + display(task["id"]) + ": " + display(task["objective"]) +
                     " — **إثبات الإنجاز:** " + display(task["verification"]))
    lines += [
        "", "## فحوص هندسية يجب التخطيط لها",
    ]
    for gate in report["conditional_gates"]:
        lines.append("- " + display(gate["id"]) + " / " + display(gate["applicability"]) +
                     ": " + display(gate["title"]) + " — اختبار: " + display(gate["test"]))
    lines += [
        "", "## قبل تسليم المشروع إلى مشرف Codex",
        "تحتاج مراجعة جدوى وتكلفة، ومراجعة هندسة وبيانات، ومراجعة أمن وAPI، ومراجعة تصميم وإتاحة استخدام،",
        "ثم مقارنة مشاريع GitHub الحقيقية وتراخيصها وتواريخ أسعار الخدمات، وربط الأدلة بملفات مراجعة قابلة للتحقق.",
        "",
        "**غير مصرح حاليًا:** تشغيل Codex تلقائيًا، دمج تغييرات، نشر الموقع، إدخال بيانات حساسة، أو دفع أي رسوم.",
        "**غير مُنجز حاليًا:** صورة فعلية للتصميم واختبارات المتصفح على تطبيق حي؛ المطلوب إنشاء مفهوم بصري بعد اعتماد المدخلات.",
        ""
    ]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Senior noncoder blueprint: research/planning only, never dispatch")
    sub = parser.add_subparsers(dest="action",required=True)
    interview = sub.add_parser("interview",help="Ask 20 Arabic questions; save PRIVATE raw answers")
    interview.add_argument("--project-id",required=True)
    interview.add_argument("--out",required=True)
    report = sub.add_parser("blueprint",help="Produce a private evidence-labeled draft from an intake file")
    report.add_argument("--input",required=True)
    report.add_argument("--out",required=True)
    report.add_argument("--markdown-out",help="Additional PRIVATE owner-readable Arabic report")
    args = parser.parse_args(argv)
    try:
        if args.action=="interview":
            interactive(args.project_id,args.out)
        else:
            data = read_private(args.input)
            report_data = evaluate(data)
            if args.markdown_out:
                primary=safe_output(args.out)
                summary=safe_output(args.markdown_out)
                if primary==summary:
                    raise IntakeError("The report and Markdown output must be separate files")
            dest=write_new(args.out,report_data)
            if args.markdown_out:
                summary=write_new(args.markdown_out,{"text":markdown_owner_report(report_data)})
                # Plain Markdown, not JSON; the output is private and not executable.
                raw=summary.read_text(encoding="utf-8")
                summary.write_text(json.loads(raw)["text"],encoding="utf-8")
            print(json.dumps({"result":"DRAFT_ONLY", "project_id":report_data["project_id"],
                "assessment":report_data["assessment_status"],
                "tasks":len(report_data["plan_draft"]), "gates":len(report_data["conditional_gates"]),
                "issues":len(report_data["skeptical_findings"]), "path":str(dest)},ensure_ascii=False))
        return 0
    except (ValueError,OSError,KeyError,TypeError,UnicodeError) as exc:
        print(json.dumps({"status":"BLOCKED","error_type":type(exc).__name__,
                          "reason":str(exc)[:180]},ensure_ascii=False),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
