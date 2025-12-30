import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.schools.models import HighSchool, University, UniversityAdmissionCriteria
from apps.consultants.models import Consultant
from apps.students.models import Student, StudentDesiredUniversity
from apps.grades.models import Grade, SubjectGrade
from apps.documents.models import Document
from apps.reports.models import ConsultationReport, ConsultationSession
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = '목업 데이터 생성'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('목업 데이터 생성을 시작합니다...'))

        # 1. 고등학교 데이터
        self.stdout.write('고등학교 데이터 생성 중...')
        schools_data = [
            {'name': '서울고등학교', 'region': '서울', 'school_type': 'PUBLIC'},
            {'name': '대일외국어고등학교', 'region': '서울', 'school_type': 'SPECIAL'},
            {'name': '민족사관고등학교', 'region': '강원', 'school_type': 'PRIVATE'},
            {'name': '부산과학고등학교', 'region': '부산', 'school_type': 'SCIENCE'},
            {'name': '인천포스코고등학교', 'region': '인천', 'school_type': 'SPECIAL'},
        ]

        high_schools = []
        for school_data in schools_data:
            school, created = HighSchool.objects.get_or_create(
                name=school_data['name'],
                defaults=school_data
            )
            high_schools.append(school)
            if created:
                self.stdout.write(f'  ✓ {school.name} 생성')

        # 2. 대학 데이터
        self.stdout.write('대학 데이터 생성 중...')
        universities_data = [
            {'name': '서울대학교', 'region': '서울', 'university_type': '국립', 'ranking': 1},
            {'name': '연세대학교', 'region': '서울', 'university_type': '사립', 'ranking': 2},
            {'name': '고려대학교', 'region': '서울', 'university_type': '사립', 'ranking': 3},
            {'name': 'KAIST', 'region': '대전', 'university_type': '국립', 'ranking': 4},
            {'name': '성균관대학교', 'region': '서울', 'university_type': '사립', 'ranking': 5},
        ]

        universities = []
        for univ_data in universities_data:
            univ, created = University.objects.get_or_create(
                name=univ_data['name'],
                defaults=univ_data
            )
            universities.append(univ)
            if created:
                self.stdout.write(f'  ✓ {univ.name} 생성')

        # 3. 입학 기준 데이터
        self.stdout.write('입학 기준 데이터 생성 중...')
        for univ in universities[:3]:
            criteria_list = [
                {
                    'university': univ,
                    'department': '컴퓨터공학과',
                    'admission_type': '학생부종합',
                    'year': 2024,
                    'criteria': {'min_gpa': 1.5, 'required_subjects': ['수학', '과학']}
                },
                {
                    'university': univ,
                    'department': '경영학과',
                    'admission_type': '학생부교과',
                    'year': 2024,
                    'criteria': {'min_gpa': 2.0, 'required_subjects': ['수학', '영어']}
                },
            ]
            for criteria_data in criteria_list:
                obj, created = UniversityAdmissionCriteria.objects.get_or_create(
                    university=criteria_data['university'],
                    department=criteria_data['department'],
                    admission_type=criteria_data['admission_type'],
                    year=criteria_data['year'],
                    defaults={'criteria': criteria_data['criteria']}
                )
                if created:
                    self.stdout.write(f'  ✓ {univ.name} {criteria_data["department"]} 기준 생성')

        # 4. 컨설턴트 사용자 및 프로필
        self.stdout.write('컨설턴트 데이터 생성 중...')
        consultants_data = [
            {'code': str(uuid.uuid4()), 'username': '김현수', 'role': 'SUPER_ADMIN', 'name': '김현수', 'specialization': '이공계'},
            {'code': str(uuid.uuid4()), 'username': '이지영', 'role': 'CONSULTANT', 'name': '이지영', 'specialization': '인문계'},
            {'code': str(uuid.uuid4()), 'username': '박민준', 'role': 'CONSULTANT', 'name': '박민준', 'specialization': '의대'},
        ]

        consultants = []
        for cons_data in consultants_data:
            user, user_created = User.objects.get_or_create(
                code=cons_data['code'],
                defaults={
                    'username': cons_data['username'],
                    'role': cons_data['role']
                }
            )
            if user_created:
                user.set_password('test1234')
                user.save()

            consultant, cons_created = Consultant.objects.get_or_create(
                user=user,
                defaults={
                    'name': cons_data['name'],
                    'phone': '010-1234-5678',
                    'specialization': cons_data['specialization']
                }
            )
            consultants.append(consultant)
            if cons_created:
                self.stdout.write(f'  ✓ 컨설턴트 {consultant.name} 생성')

        # 5. 학생 데이터
        self.stdout.write('학생 데이터 생성 중...')
        students_data = [
            {'name': '김민지', 'student_code': 'STU001', 'grade': '3', 'high_school': high_schools[0], 'consultant': consultants[0]},
            {'name': '이준호', 'student_code': 'STU002', 'grade': '3', 'high_school': high_schools[1], 'consultant': consultants[1]},
            {'name': '박서연', 'student_code': 'STU003', 'grade': '2', 'high_school': high_schools[2], 'consultant': consultants[2]},
            {'name': '최동욱', 'student_code': 'STU004', 'grade': '3', 'high_school': high_schools[0], 'consultant': consultants[0]},
            {'name': '정하늘', 'student_code': 'STU005', 'grade': '2', 'high_school': high_schools[1], 'consultant': consultants[1]},
        ]

        students = []
        for stud_data in students_data:
            student, created = Student.objects.get_or_create(
                student_code=stud_data['student_code'],
                defaults={
                    **stud_data,
                    'phone': '010-9876-5432',
                    'parent_phone': '010-8765-4321',
                    'status': 'ACTIVE'
                }
            )
            students.append(student)
            if created:
                self.stdout.write(f'  ✓ 학생 {student.name} 생성')

        # 6. 학생 지망 대학
        self.stdout.write('지망 대학 데이터 생성 중...')
        for i, student in enumerate(students[:3]):
            desired_data = [
                {'student': student, 'university': universities[i], 'department': '컴퓨터공학과', 'priority': 'FIRST'},
                {'student': student, 'university': universities[i+1], 'department': '경영학과', 'priority': 'SECOND'},
            ]
            for desired in desired_data:
                obj, created = StudentDesiredUniversity.objects.get_or_create(
                    student=desired['student'],
                    university=desired['university'],
                    department=desired['department'],
                    defaults=desired
                )
                if created:
                    self.stdout.write(f'  ✓ {student.name}의 지망 대학 {desired["university"].name} 추가')

        # 7. 성적 데이터
        self.stdout.write('성적 데이터 생성 중...')
        for student in students[:3]:
            grade_data = {
                'student': student,
                'semester': '3-1',
                'exam_type': 'MIDTERM',
                'gpa': Decimal('2.5'),
                'korean_score': 85,
                'korean_grade': 2,
                'math_score': 90,
                'math_grade': 1,
                'english_score': 88,
                'english_grade': 2,
                'total_score': 263,
                'percentile': Decimal('85.5')
            }
            grade, created = Grade.objects.get_or_create(
                student=student,
                semester='3-1',
                exam_type='MIDTERM',
                defaults=grade_data
            )
            if created:
                self.stdout.write(f'  ✓ {student.name}의 성적 생성')

                # 과목별 성적
                SubjectGrade.objects.create(
                    grade=grade,
                    subject_name='국어',
                    raw_score=Decimal('85.0'),
                    grade_rank=Decimal('2.0'),
                    class_rank=5,
                    class_total=30
                )

        # 8. 컨설팅 리포트
        self.stdout.write('컨설팅 리포트 데이터 생성 중...')
        for student in students[:2]:
            report_data = {
                'student': student,
                'consultant': student.consultant,
                'report_type': 'MONTHLY',
                'title': f'{student.name} 학생 월간 리포트',
                'summary': '이번 달 학습 진행 상황 요약',
                'content': '상세 내용...',
                'status': 'COMPLETED'
            }
            report, created = ConsultationReport.objects.get_or_create(
                student=student,
                consultant=student.consultant,
                report_type='MONTHLY',
                defaults=report_data
            )
            if created:
                self.stdout.write(f'  ✓ {student.name}의 리포트 생성')

        # 9. 상담 세션
        self.stdout.write('상담 세션 데이터 생성 중...')
        from django.utils import timezone
        for student in students[:2]:
            session_data = {
                'student': student,
                'consultant': student.consultant,
                'session_type': 'ONLINE',
                'session_date': timezone.now(),
                'duration_minutes': 60,
                'notes': '학습 계획 및 진로 상담'
            }
            session, created = ConsultationSession.objects.get_or_create(
                student=student,
                consultant=student.consultant,
                session_date__date=timezone.now().date(),
                defaults=session_data
            )
            if created:
                self.stdout.write(f'  ✓ {student.name}의 상담 세션 생성')

        self.stdout.write(self.style.SUCCESS('\n✓ 모든 목업 데이터 생성이 완료되었습니다!'))
        self.stdout.write(self.style.SUCCESS(f'  - 고등학교: {HighSchool.objects.count()}개'))
        self.stdout.write(self.style.SUCCESS(f'  - 대학: {University.objects.count()}개'))
        self.stdout.write(self.style.SUCCESS(f'  - 컨설턴트: {Consultant.objects.count()}명'))
        self.stdout.write(self.style.SUCCESS(f'  - 학생: {Student.objects.count()}명'))
        self.stdout.write(self.style.SUCCESS(f'  - 성적: {Grade.objects.count()}개'))
        self.stdout.write(self.style.SUCCESS(f'  - 리포트: {ConsultationReport.objects.count()}개'))
