from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
# from here down is what I added to django
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from .forms import TodoForm
from .models import Todo
# login required to access pages only if a use is logged in
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    return render(request, "todo/home.html")


def signupuser(request):
    # Check request object if method=post or get
    if request.method == 'GET':
        # Use django forms (built-in)
        # form input checking must be applied by the developer,it won't be applied automatically
        return render(request, "todo/signupuser.html", {'form': UserCreationForm()})
    else:
        # If Post confirm passwords and create a new user
        if request.POST['password1'] == request.POST['password2']:
            # try/except catches the error of unique inputs
            try:
                # makes user object
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                # save inserts the object to database
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, "todo/signupuser.html", {'form': UserCreationForm(), 'error': 'Username already exists.'})

        else:
            # Display a message to user that passwords didn't match
            return render(request, "todo/signupuser.html", {'form': UserCreationForm(), 'error': 'Passwords did not match.'})


# list the todos of the current user
@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, dateCompleted__isnull=True)
    return render(request, "todo/currenttodos.html", {'todos': todos})


@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, dateCompleted__isnull=False).order_by('dateCompleted')
    return render(request, "todo/completedtodos.html", {'todos': todos})


@login_required
def logoutuser(request):
    # Browsers load all the <a> pages in the page you asked for
    # so the if condition makes sure that if we have a logout button browser won't logout directly when logging in
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def loginuser(request):
    if request.method == 'GET':
        return render(request, "todo/loginuser.html", {'form': AuthenticationForm()})
    else:
        user = authenticate(request,username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': 'Username and Password was not found.'})
        else:
            login(request, user)
            return redirect('currenttodos')


@login_required
def createtodo(request):
    if request.method == 'GET':
        #TodoForm was created in addition to forms.py file
        return render(request, "todo/createtodo.html", {'form': TodoForm()})
    else:
        # catch error like value errors - in example: title length
        try:
            # create a new todoobject
            form = TodoForm(request.POST)
            # commit=False means don't put it in database
            newtodo = form.save(commit=False)
            # use the current user to add the todoobject to his todos
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form': TodoForm(), 'error': 'Bad data entered.'})

'''
view the selected to todo from todoslist
'''
@login_required
def viewtodo(request, todo_pk):
    # get object where pk = todo_pk and user = request user (logged in user)
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            # create a new todoobject
            # adding instance parameter will help it know that this is an existing object to update
            form = TodoForm(request.POST, instance=todo)
            # commit=False means don't put it in database
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form, 'error': 'Bad input.'})


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        # updating the date completed to current time
        todo.dateCompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')


