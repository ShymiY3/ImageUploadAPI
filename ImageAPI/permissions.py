from rest_framework.permissions import BasePermission

class HasTier(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not hasattr(user, 'tier'):
            return False
        if not user.tier is None:
            return True
        return False

class IsOwnerOrStaf(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True 
        return obj.owner == request.user
        
class CanGenerateExpiringLink(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        
        if request.user.is_staff:
            return True
        
        if not hasattr(user, 'tier'):
            return False    
        
        return request.user.tier.generate_expiring_link