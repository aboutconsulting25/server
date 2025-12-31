from rest_framework import serializers
from .models import Grade, SubjectGrade
from apps.students.serializers import StudentListSerializer


class SubjectGradeSerializer(serializers.ModelSerializer):
    """과목별 성적 시리얼라이저"""

    class Meta:
        model = SubjectGrade
        fields = [
            'id', 'grade', 'subject_name', 'raw_score', 'standard_score',
            'grade_rank', 'percentile', 'class_rank', 'class_total',
            'grade_rank_in_school', 'grade_total_in_school',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GradeSerializer(serializers.ModelSerializer):
    """성적 시리얼라이저"""
    student_detail = StudentListSerializer(source='student', read_only=True)
    subject_grades = SubjectGradeSerializer(many=True, read_only=True)
    average_grade_calculated = serializers.DecimalField(
        source='average_grade',
        max_digits=4,
        decimal_places=2,
        read_only=True
    )

    # 등급 변환 필드 (9등급제 ↔ 5등급제)
    korean_grade_5 = serializers.FloatField(read_only=True)
    korean_grade_9 = serializers.FloatField(read_only=True)
    math_grade_5 = serializers.FloatField(read_only=True)
    math_grade_9 = serializers.FloatField(read_only=True)
    english_grade_5 = serializers.FloatField(read_only=True)
    english_grade_9 = serializers.FloatField(read_only=True)
    science1_grade_5 = serializers.FloatField(read_only=True)
    science1_grade_9 = serializers.FloatField(read_only=True)
    science2_grade_5 = serializers.FloatField(read_only=True)
    science2_grade_9 = serializers.FloatField(read_only=True)
    history_grade_5 = serializers.FloatField(read_only=True)
    history_grade_9 = serializers.FloatField(read_only=True)

    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_detail', 'semester', 'exam_type',
            'gpa', 'korean_score', 'korean_grade', 'math_score', 'math_grade',
            'english_score', 'english_grade', 'science1_score', 'science1_grade',
            'science2_score', 'science2_grade', 'history_score', 'history_grade',
            'total_score', 'percentile', 'average_grade_calculated',
            'korean_grade_5', 'korean_grade_9',
            'math_grade_5', 'math_grade_9',
            'english_grade_5', 'english_grade_9',
            'science1_grade_5', 'science1_grade_9',
            'science2_grade_5', 'science2_grade_9',
            'history_grade_5', 'history_grade_9',
            'subject_grades', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GradeListSerializer(serializers.ModelSerializer):
    """성적 목록용 간단한 시리얼라이저"""
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_name', 'semester',
            'exam_type', 'gpa', 'total_score'
        ]
        read_only_fields = ['id']


class GradeCreateSerializer(serializers.ModelSerializer):
    """성적 생성용 시리얼라이저"""
    subject_grades = SubjectGradeSerializer(many=True, required=False)

    class Meta:
        model = Grade
        fields = [
            'student', 'semester', 'exam_type', 'gpa',
            'korean_score', 'korean_grade', 'math_score', 'math_grade',
            'english_score', 'english_grade', 'science1_score', 'science1_grade',
            'science2_score', 'science2_grade', 'history_score', 'history_grade',
            'total_score', 'percentile', 'notes', 'subject_grades'
        ]

    def create(self, validated_data):
        subject_grades_data = validated_data.pop('subject_grades', [])
        grade = Grade.objects.create(**validated_data)

        # 과목별 성적 생성
        for subject_data in subject_grades_data:
            SubjectGrade.objects.create(grade=grade, **subject_data)

        return grade
