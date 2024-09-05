from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.


def home(request):  # renderiza lo que esté en el archivo de home.html
    return render(request, 'home.html')


def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })  # renderiza todo lo que esté en el archivo signup.html
    else:
        # compara si las contraseñas son iguales
        if request.POST['password1'] == request.POST['password2']:
            try:
                # registra el usuario
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()  # <----- Guarda en la base de datos
                # <--- crea una cookie para guardar la sesión
                login(request, user)
                # el return es para que no siga a la orden de proyectar "passwords does not match"
                return redirect('tasks')

            except IntegrityError:  # revisa que el usuario ya exista en la base de datos, si existe muestra un error
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Username already exists !'
                })

        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Passwords does not match!'
        })  # revisa que las contraseñas coincidan en el formulario, si no lo hacen mostrará una pantalla de error

@login_required
def tasks(request):
    # filtra las tareas por usuario en el FE
    tasks = Task.objects.filter(user=request.user, datecompleated__isnull=True)
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_completed(request):
    # filtra las tareas por usuario en el FE
    tasks = Task.objects.filter(user=request.user, datecompleated__isnull=False).order_by('-datecompleated')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def create_tasks(request):
    if request.method == "GET":
        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:  # valida que todos los datos estén completos, revisa que la página no sea adulterada
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user  # revisa que los datos sean válidos
            new_task.save()
            print(new_task)
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,  # recarga la página en caso que la misma sea adulterada
                'error': 'Please provide valid data'
            })

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        # get_object_or_404 sirve para que el servidor no se caiga en caso de que el objeto no exista
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error':"Error Updating Task..."})


@login_required
def completeTask(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleated = timezone.now()
        task.save()
        return redirect('tasks')
    
@login_required
def deleteTask(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')


@login_required
def signout(request):
    # sirve para borrar la cookie de sesión y devolver a la página de inicio de sesión
    logout(request)
    return redirect(home)


def sign_in(request):
    if request.method == 'GET':  # muestra el formulario de inicio de sesión
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:  # esto de aquí corrobora las creedenciales que sean correctas
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])

        if user is None:  # si las creedenciales son inceorrectas mostrará error
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect!'
            })
        else:  # si son correctas se mostrará la página "tasks"
            login(request, user)
            return redirect('tasks')
