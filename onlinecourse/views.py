from django.shortcuts import render
from django.http import HttpResponseRedirect
# <HINT> Import any new Models here
from .models import Course, Enrollment, Submission, Question, Choice
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# <HINT> Create a submit view to create an exam submission record for a course enrollment,
# you may implement it based on following logic:
         # Get user and course object, then get the associated enrollment object created when the user enrolled the course
         # Create a submission object referring to the enrollment
         # Collect the selected choices from exam form
         # Add each selected choice object to the submission object
         # Redirect to show_exam_result with the submission id
def submit(request, course_id):
    enrollment = Enrollment.objects.get(user=request.user, course = course_id)
    choice_ids = extract_answers(request)
    choices = Choice.objects.filter(id__in = choice_ids)

    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(choices)    

    return HttpResponseRedirect(reverse(viewname='onlinecourse:show_exam_result', args=(course_id, submission.id,)))


# <HINT> A example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
    submitted_anwsers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_anwsers.append(choice_id)
    
    print (submitted_anwsers)
    return submitted_anwsers


# <HINT> Create an exam result view to check if learner passed exam and show their question results and result for each question,
# you may implement it based on the following logic:
        # Get course and submission based on their ids
        # Get the selected choice ids from the submission record
        # For each selected choice, check if it is a correct answer or not
        # Calculate the total score
def show_exam_result(request, course_id, submission_id):
    course = Course.objects.get(id=course_id)
    submission = Submission.objects.get(id=submission_id)

    choices = submission.choices.all()
    choice_ids = choices.values_list('id', flat=True)

    questions = Question.objects.filter(lesson__course = course)

    score = 0
    max_score = 0
    exam_result = {}
    awr = 0     #0 - wrong, not checked
                #1 - wrong, checked
                #2 - right, not checked
                #3 - right, checked

    for q in questions:
        max_score += q.grade
        q_ch = {}
        q_answered = True

        for ch in q.choice_set.all():
            
            if ((not ch.is_correct) and (ch.id in choice_ids)):     #wrong answer checked
                awr = 1
                q_answered = False
            elif (ch.is_correct and (ch.id not in choice_ids)):     #right answer not checked
                awr = 2
                q_answered = False
            elif ((not ch.is_correct) and (ch.id not in choice_ids)):    #wrong answer not checked
                awr = 0
            else:                                                        #right answer checked
                awr = 3

            q_ch[ch.choice_text] = awr              #add to row dict a pair {'choice_text : awr'}

        exam_result[q.question_text] = q_ch          #add a row

        if q_answered:
            score += q.grade 

    print(exam_result)

    context = {
        'course_id' : course_id,
        'grade' : int(score/max_score*100),
        'exam_result' : exam_result,
    }

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)







