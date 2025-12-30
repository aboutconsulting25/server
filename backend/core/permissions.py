from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """대표 컨설턴트(SUPER_ADMIN) 권한"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'SUPER_ADMIN'


class IsConsultant(permissions.BasePermission):
    """컨설턴트(CONSULTANT) 권한"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['CONSULTANT', 'SUPER_ADMIN']


class IsSchoolAdmin(permissions.BasePermission):
    """학원 관리자(SCHOOL_ADMIN) 권한"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['SCHOOL_ADMIN', 'SUPER_ADMIN']


class IsSales(permissions.BasePermission):
    """영업 사원(SALES) 권한"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['SALES', 'SUPER_ADMIN']


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    객체의 소유자만 수정 가능, 나머지는 읽기 전용
    """

    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 모든 인증된 사용자에게 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 쓰기 권한은 소유자에게만 허용
        return obj.user == request.user


class IsConsultantOrSuperAdmin(permissions.BasePermission):
    """
    컨설턴트 또는 대표 컨설턴트만 접근 가능
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['CONSULTANT', 'SUPER_ADMIN']
        )


class IsAssignedConsultantOrSuperAdmin(permissions.BasePermission):
    """
    담당 컨설턴트 또는 대표 컨설턴트만 접근 가능
    """

    def has_object_permission(self, request, view, obj):
        # SUPER_ADMIN은 모든 접근 허용
        if request.user.role == 'SUPER_ADMIN':
            return True

        # 객체에 consultant 필드가 있는 경우
        if hasattr(obj, 'consultant'):
            return obj.consultant and obj.consultant.user == request.user

        # 객체에 student 필드가 있는 경우 (성적, 서류 등)
        if hasattr(obj, 'student'):
            return (
                obj.student.consultant and
                obj.student.consultant.user == request.user
            )

        return False


class CanManageStudents(permissions.BasePermission):
    """
    학생 관리 권한 (컨설턴트, 학원 관리자, 대표 컨설턴트)
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['CONSULTANT', 'SCHOOL_ADMIN', 'SUPER_ADMIN']
        )


class CanViewReports(permissions.BasePermission):
    """
    리포트 조회 권한 (모든 인증된 사용자)
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return False


class CanManageReports(permissions.BasePermission):
    """
    리포트 관리 권한 (컨설턴트, 대표 컨설턴트)
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['CONSULTANT', 'SUPER_ADMIN']
        )
