from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Quiz
from .serializers import QuizSerializer


class QuizView(APIView):

   def get(self, request):

      quizzes = Quiz.objects.all()

      serializer = QuizSerializer(
         quizzes,
         many=True
      )

      return Response(
         serializer.data,
         status=status.HTTP_200_OK
      )

   def post(self, request):

      if not request.user.is_authenticated or not request.user.is_staff:
         return Response(
               {
                  "detail": "Admin access required."
               },
               status=status.HTTP_403_FORBIDDEN
         )

      serializer = QuizSerializer(
         data=request.data
      )

      if serializer.is_valid():

         serializer.save()

         return Response(
               serializer.data,
               status=status.HTTP_201_CREATED
         )

      return Response(
         serializer.errors,
         status=status.HTTP_400_BAD_REQUEST
      )


class QuizDetailView(APIView):

   def get_object(self, pk):

      try:
         return Quiz.objects.get(pk=pk)

      except Quiz.DoesNotExist:
         return None

   def get(self, request, pk):

      quiz = self.get_object(pk)

      if quiz is None:
         return Response(
               {
                  "detail": "Quiz not found."
               },
               status=status.HTTP_404_NOT_FOUND
         )

      serializer = QuizSerializer(quiz)

      return Response(
         serializer.data,
         status=status.HTTP_200_OK
      )

   def patch(self, request, pk):

      quiz = self.get_object(pk)

      if quiz is None:
         return Response(
               {
                  "detail": "Quiz not found."
               },
               status=status.HTTP_404_NOT_FOUND
         )

      serializer = QuizSerializer(
         quiz,
         data=request.data,
         partial=True
      )

      if serializer.is_valid():

         serializer.save()

         return Response(
               serializer.data,
               status=status.HTTP_200_OK
         )

      return Response(
         serializer.errors,
         status=status.HTTP_400_BAD_REQUEST
      )

   def delete(self, request, pk):
      quiz = self.get_object(pk)
      if quiz is None:
         return Response(
               {
                  "detail": "Quiz not found."
               },
               status=status.HTTP_404_NOT_FOUND
         )

      quiz.delete()
      return Response(
         {
               "detail": "Quiz deleted successfully."
         },
         status=status.HTTP_200_OK
      )
