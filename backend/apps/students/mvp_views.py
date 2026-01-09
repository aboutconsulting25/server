"""
MVP 전용 원포인트 API

1차 MVP를 위한 통합 엔드포인트
- 생기부 등록부터 분석까지 한 번에 처리
"""
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample, inline_serializer

from apps.students.models import Student
from apps.documents.models import Document, DocumentAnalysis
from apps.reports.models import ConsultationReport
from apps.reports.ai_module import (
    analyze_document_with_ai,
    get_mock_grade_analysis,
    get_mock_comprehensive_analysis
)


@extend_schema(
    tags=['MVP'],
    summary='생기부 등록 원포인트 API (MVP용)',
    description='''
    생기부 등록부터 분석까지 한 번에 처리하는 원포인트 API

    **처리 과정:**
    1. 학생 정보 생성 (이름, 계열, 희망 대학/학과)
    2. 생기부 PDF 업로드
    3. AI 분석 실행 (목업 또는 실제 AI 모듈)
    4. 리포트 생성
    5. 분석 결과 ID 반환

    **반환값:**
    - student_id: 생성된 학생 ID
    - document_id: 업로드된 생기부 문서 ID
    - analysis_id: 생기부 분석 결과 ID
    - report_id: 종합 리포트 ID

    **다음 단계:**
    - GET /api/v1/documents/{document_id}/latest-analysis/ → 생기부 분석 조회
    - GET /api/v1/grades/student-grade-analysis/?student_id={student_id} → 성적 분석 조회
    - GET /api/v1/reports/{report_id}/comprehensive-analysis/ → 종합 분석 조회
    ''',
    request=inline_serializer(
        name='RegisterSaenggibuRequest',
        fields={
            'name': serializers.CharField(help_text='학생 이름'),
            'major_track': serializers.ChoiceField(
                choices=['HUMANITIES', 'SCIENCE', 'ART'],
                help_text='계열 (HUMANITIES: 인문계, SCIENCE: 자연계, ART: 예체능)'
            ),
            'desired_universities': serializers.CharField(
                help_text='희망 대학/학과 JSON 배열 (예: [{"university":"서울대","department":"컴공"},{"university":"연대","department":"전전"}])'
            ),
            'file': serializers.FileField(help_text='생기부 PDF 파일'),
            'use_mock': serializers.BooleanField(
                required=False,
                default=True,
                help_text='목업 데이터 사용 여부 (기본값: true, AI 모듈 연결 시 false)'
            ),
        }
    ),
    examples=[
        OpenApiExample(
            'Success Response',
            value={
                "success": True,
                "message": "생기부 등록 및 분석이 완료되었습니다.",
                "data": {
                    "student_id": "uuid",
                    "student_name": "홍길동",
                    "document_id": "uuid",
                    "analysis_id": "uuid",
                    "report_id": "uuid",
                    "next_steps": {
                        "생기부_분석": "/api/v1/documents/{document_id}/latest-analysis/",
                        "성적_분석": "/api/v1/grades/student-grade-analysis/?student_id={student_id}",
                        "종합_분석": "/api/v1/reports/{report_id}/comprehensive-analysis/"
                    }
                }
            }
        )
    ]
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def register_saenggibu_onestop(request):
    """
    생기부 등록 원포인트 API (MVP용)

    학생 생성 → 생기부 업로드 → AI 분석 → 리포트 생성을 한 번에 처리
    """
    # 1. 입력 검증
    name = request.data.get('name')
    major_track = request.data.get('major_track')
    desired_universities_str = request.data.get('desired_universities')
    file = request.FILES.get('file')
    use_mock = request.data.get('use_mock', 'true').lower() == 'true'

    if not all([name, major_track, desired_universities_str, file]):
        return Response({
            'success': False,
            'error': 'name, major_track, desired_universities, file are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # PDF 파일 검증
    if file.content_type not in ['application/pdf']:
        return Response({
            'success': False,
            'error': 'PDF 파일만 업로드 가능합니다.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 파일 크기 검증 (50MB 제한)
    max_size = 50 * 1024 * 1024  # 50MB
    if file.size > max_size:
        return Response({
            'success': False,
            'error': 'PDF 파일 크기는 50MB를 초과할 수 없습니다.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # desired_universities JSON 파싱
    import json
    try:
        desired_universities = json.loads(desired_universities_str)
        if not isinstance(desired_universities, list) or len(desired_universities) == 0:
            raise ValueError("desired_universities must be a non-empty array")
    except (json.JSONDecodeError, ValueError) as e:
        return Response({
            'success': False,
            'error': f'Invalid desired_universities format: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 2. 트랜잭션으로 처리
    try:
        with transaction.atomic():
            # 2-1. 학생 생성
            student_code = f"STU-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            student = Student.objects.create(
                name=name,
                student_code=student_code,
                major_track=major_track,
                desired_universities_text=desired_universities,
                grade='3',  # 기본값 (추후 입력 받을 수 있음)
                status='ACTIVE'
            )

            # 2-2. 생기부 문서 메타데이터 생성 (S3 연결 전까지는 파일 저장 안 함)
            # PDF 파일은 AI 모듈로만 전달하고, 메타데이터만 DB에 저장
            document = Document.objects.create(
                student=student,
                document_type='생기부',
                title=f"{name} 생활기록부",
                # file=None  # S3 연결 전까지는 파일 저장하지 않음
                file_size=file.size,
                mime_type=file.content_type,
                status='PROCESSING'
            )

            # 2-3. AI 분석 실행 (PDF 파일을 AI 모듈로 전달)
            # PDF 파일을 메모리에서 AI 모듈로 직접 전달 (OCR + 분석)
            # use_mock과 관계없이 항상 PDF 파일을 전달 (AI 모듈에서 처리 여부 결정)
            saenggibu_analysis = analyze_document_with_ai(file)

            # DocumentAnalysis 생성
            analysis = DocumentAnalysis.objects.create(
                document=document,
                student=student,
                status='COMPLETED',
                analysis_result=saenggibu_analysis,
                started_at=timezone.now(),
                completed_at=timezone.now()
            )

            # 문서 상태 업데이트
            document.status = 'COMPLETED'
            document.save()

            # 2-4. 리포트 생성 (성적 분석 + 종합 분석)
            if use_mock:
                grade_analysis = get_mock_grade_analysis()
                comprehensive_analysis = get_mock_comprehensive_analysis()
            else:
                # TODO: 실제 AI 모듈 호출
                grade_analysis = get_mock_grade_analysis()
                comprehensive_analysis = get_mock_comprehensive_analysis()

            report = ConsultationReport.objects.create(
                student=student,
                report_type='INITIAL',
                title=f"{name} 초기 상담 리포트",
                summary=f"{name} 학생의 생기부 분석 및 종합 컨설팅 리포트",
                content="AI 분석을 통한 종합 리포트",
                ai_insights={
                    '성적분석': grade_analysis,
                    '종합분석': comprehensive_analysis
                },
                university_analysis=comprehensive_analysis.get('수시카드', {}),
                status='COMPLETED'
            )

            # 3. 응답 생성
            return Response({
                'success': True,
                'message': '생기부 등록 및 분석이 완료되었습니다.',
                'data': {
                    'student_id': str(student.id),
                    'student_name': student.name,
                    'student_code': student.student_code,
                    'major_track': student.major_track,
                    'desired_universities': student.desired_universities_text,
                    'document_id': str(document.id),
                    'analysis_id': str(analysis.id),
                    'report_id': str(report.id),
                    'next_steps': {
                        '생기부_분석': f'/api/v1/documents/{document.id}/latest-analysis/',
                        '성적_분석': f'/api/v1/grades/student-grade-analysis/?student_id={student.id}',
                        '종합_분석': f'/api/v1/reports/{report.id}/comprehensive-analysis/'
                    }
                }
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'success': False,
            'error': f'처리 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
