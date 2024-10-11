from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from users.serializers import AvatarSerializer

User = get_user_model()


class AvatarDetail(generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = AvatarSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
