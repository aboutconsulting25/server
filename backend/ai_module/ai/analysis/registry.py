# ai/analysis/registry.py

PROMPT_REGISTRY = {

    # ==================================================
    # 1️⃣ 성적 강점 / 약점 요약
    # ==================================================
    "grade_strength_weakness": {
        "prompt_file": "grade/grade_strength_weakness",
        "model": "gpt-4.1-mini",

        "required_student_info": [
            "name",
            "grade",
            "semester",
            "targets",
        ],
        "required_ocr": [
            "grade_text",
        ],

        "input_builder": lambda c, o: f"""
[학생 정보]
- 이름: {c["name"]}
- 학년/학기: {c["grade"]} {c["semester"]}

[지망 학교-학과]
{chr(10).join(f"- {t['school']} {t['major']}" for t in c["targets"])}

[학년/학기별 성적 데이터]
{o["grade_text"]}

[요청]
위 정보를 바탕으로 성적 강점과 성적 약점을 도출하라.
        """.strip(),

        "save_key": "grade_strength_weakness",
    },

    # ==================================================
    # 2️⃣ 교과 성적 심층 분석
    # ==================================================
    "grade_in_depth_analysis": {
        "prompt_file": "grade/grade_in_depth_analysis",
        "model": "gpt-4.1-mini",

        "required_student_info": [
            "name",
            "grade",
            "semester",
        ],
        "required_ocr": [
            "grade_text",
        ],

        "input_builder": lambda c, o: f"""
[학생 정보]
- 이름: {c["name"]}
- 학년/학기: {c["grade"]} {c["semester"]}

[학년/학기별 성적 데이터]
{o["grade_text"]}

[요청]
위 성적 데이터를 바탕으로
국어, 수학, 영어, 사회, 과학, 교양
7개 영역에 대한 성적 심층 분석을 작성하라.
        """.strip(),

        "save_key": "grade_in_depth_analysis",
    },

    # ==================================================
    # 3️⃣ 생활기록부 강점 / 약점 요약
    # ==================================================
    "life_record_strength_weakness": {
        "prompt_file": "life_record/strength_weakness_summary",
        "model": "gpt-4.1-mini",

        "required_student_info": [
            "name",
            "targets",
        ],
        "required_ocr": [
            "detail_ability",
            "life_record_tables",
            "overall_opinion",
        ],

        "input_builder": lambda c, o: f"""
[학생 정보]
- 이름: {c["name"]}

[지망 학교-학과]
{chr(10).join(f"- {t['school']} {t['major']}" for t in c["targets"])}

[생활기록부 발췌]
- 세부능력 및 특기사항
{o["detail_ability"]}

- 창의적 체험활동
{o["life_record_tables"]}

- 행동특성 및 종합의견
{o["overall_opinion"]}

[요청]
위 생활기록부 내용을 바탕으로
강점 요약과 약점 요약을 도출하라.
        """.strip(),

        "save_key": "life_record_strength_weakness",
    },

    # ==================================================
    # 4️⃣ 생활기록부 진단 개요
    # ==================================================
    "life_record_diagnosis_overview": {
        "prompt_file": "life_record/diagnosis_overview",
        "model": "gpt-4.1-mini",

        "required_student_info": [
            "name",
            "targets",
        ],
        "required_ocr": [
            "grade_text",
            "detail_ability",
            "life_record_tables",
            "overall_opinion",
        ],

        "input_builder": lambda c, o: f"""
[학생 정보]
- 이름: {c["name"]}

[지망 학교-학과]
{chr(10).join(f"- {t['school']} {t['major']}" for t in c["targets"])}

[학년/학기별 성적 데이터]
{o["grade_text"]}

[생활기록부 발췌]
{o["detail_ability"]}
{o["life_record_tables"]}
{o["overall_opinion"]}

[요청]
위 생활기록부 내용을 바탕으로
진단 개요를 도출하라.
        """.strip(),

        "save_key": "life_record_diagnosis_overview",
    },

    # ==================================================
    # 5️⃣ 진로적합성 강화 로드맵 – 교과 성적
    # ==================================================
    "life_record_roadmap_academic": {
        "prompt_file": "life_record/roadmap_academic",
        "model": "gpt-4.1-mini",

        "required_student_info": [
            "targets",
        ],
        "required_ocr": [
            "detail_ability",
            "life_record_tables",
            "overall_opinion",
        ],

        "input_builder": lambda c, o: f"""
[지망 학교-학과]
{chr(10).join(f"- {t['school']} {t['major']}" for t in c["targets"])}

[생활기록부 발췌]
{o["detail_ability"]}
{o["life_record_tables"]}
{o["overall_opinion"]}

[요청]
위 생활기록부 내용을 바탕으로
진로적합성 강화 로드맵 중
'교과 성적' 섹션을 작성하라.
        """.strip(),

        "save_key": "academic_roadmap",
    },

    # ==================================================
    # 6️⃣ 심화 보고서 / 프로젝트 추천 -> 이건 아직 RAG 적용을 안했습니다!
    # ==================================================
    "project_recommendation": {
        "prompt_file": "recommendation/project_recommendation",
        "model": "gpt-4.1-mini",

        "required_student_info": [
            "targets",
        ],
        "required_ocr": [
            "detail_ability",
            "life_record_tables",
            "overall_opinion",
            #"papers_block",
        ],

        "input_builder": lambda c, o: f"""
[지망 학교-학과]
{chr(10).join(f"- {t['school']} {t['major']}" for t in c["targets"])}

[생활기록부 발췌]
{o["detail_ability"]}
{o["life_record_tables"]}
{o["overall_opinion"]}

[논문 목록]
{o.get(
    "papers_block",
    "※ 현재는 RAG 기반 논문 추천을 제공하지 않습니다."
)}

[요청]
위 정보를 바탕으로
심화 보고서/심화 프로젝트 3가지를 추천하라.
        """.strip(),

        "save_key": "project_recommendations",
    },

    # ==================================================
    # 7️⃣ 진로 관련 도서 추천 -> 이건 아직 RAG 적용을 안했습니다!
    # ==================================================
    "book_recommendation": {
        "prompt_file": "recommendation/book_recommendation",
        "model": "gpt-4.1-mini",

        "required_student_info": [
            "targets",
        ],
        "required_ocr": [
            "detail_ability",
            "life_record_tables",
            "overall_opinion",
            #"books_block",
        ],

        "input_builder": lambda c, o: f"""
[지망 학교-학과]
{chr(10).join(f"- {t['school']} {t['major']}" for t in c["targets"])}

[생활기록부 발췌]
{o["detail_ability"]}
{o["life_record_tables"]}
{o["overall_opinion"]}

[도서 후보 목록]
{o.get(
    "books_block",
    "※ 현재는 RAG 기반 도서 추천을 제공하지 않습니다."
)}


[요청]
위 정보를 바탕으로
진로 관련 도서 3권을 추천하라.
        """.strip(),

        "save_key": "career_book_recommendations",
    },

    # ==================================================
    # 8️⃣ 학부모 조언 & 학생 응원 메시지
    # ==================================================
    "parent_student_message": {
        "prompt_file": "message/parent_student_message",
        "model": "gpt-4.1-mini",

        "required_student_info": [
            "name",
            "targets",
        ],
        "required_ocr": [
            "grade_text",
            "detail_ability",
            "life_record_tables",
            "overall_opinion",
        ],

        "input_builder": lambda c, o: f"""
[학생 정보]
- 이름: {c["name"]}

[지망 학교-학과]
{chr(10).join(f"- {t['school']} {t['major']}" for t in c["targets"])}

[학년/학기별 성적 데이터]
{o["grade_text"]}

[생활기록부 발췌]
{o["detail_ability"]}
{o["life_record_tables"]}
{o["overall_opinion"]}

[요청]
학부모님께 드리는 조언과
학생에게 전하는 응원의 메시지를 작성하라.
        """.strip(),

        "save_key": "parent_student_message",
    },
}
