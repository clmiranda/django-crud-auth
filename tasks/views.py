from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.


def home(request):
    return render(request, "home.html")


def signup(request):
    if request.method == "GET":
        return render(request, "signup.html", {"form": UserCreationForm})
    else:
        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    username=request.POST["username"],
                    password=request.POST["password1"],
                )
                user.save()
                login(request, user)
                messages.add_message(
                    request,
                    messages.INFO,
                    "Usuario registrado y sesión iniciada correctamente",
                )
                return redirect("tasks")
            except IntegrityError:
                return render(
                    request,
                    "signup.html",
                    {
                        "form": UserCreationForm,
                        "error": "El nombre de usuario ya existe",
                    },
                )
        return render(
            request,
            "signup.html",
            {"form": UserCreationForm, "error": "Las contraseñas no coinciden"},
        )


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, dateCompleted__isnull=True).order_by(
        "-dateCompleted"
    )
    return render(request, "tasks.html", {"tasks": tasks, "typeTask": "Pendientes"})


@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(
        user=request.user, dateCompleted__isnull=False
    ).order_by("-dateCompleted")
    return render(request, "tasks.html", {"tasks": tasks, "typeTask": "Completadas"})


@login_required
def create_task(request):
    if request.method == "GET":
        return render(request, "create_task.html", {"form": TaskForm})
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            messages.add_message(request, messages.INFO, "Tarea creada correctamente")
            return redirect("tasks")
        except ValueError:
            return render(
                request,
                "create_task.html",
                {"form": TaskForm, "error": "Debe completar los campos"},
            )


@login_required
def task_detail(request, task_id):
    if request.method == "GET":
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, "task_detail.html", {"task": task, "form": form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            messages.add_message(request, messages.INFO, "Datos actualizados")
            return (
                redirect("tasks")
                if not task.dateCompleted
                else redirect("tasks_completed")
            )
        except ValueError:
            return render(
                request,
                "task_detail.html",
                {"task": task, "form": form, "error": "Error al actualizar los datos"},
            )


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":
        task.dateCompleted = timezone.now()
        task.save()
        messages.add_message(request, messages.INFO, "Tarea marcada como completada")
        return redirect("tasks")


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":
        task.delete()
        messages.add_message(request, messages.INFO, "Tarea eliminada")
        return (
            redirect("tasks") if not task.dateCompleted else redirect("tasks_completed")
        )


@login_required
def signout(request):
    logout(request)
    messages.add_message(request, messages.INFO, "Saliendo de la aplicación")
    return redirect("home")


def signin(request):
    if request.method == "GET":
        return render(request, "signin.html", {"form": AuthenticationForm})
    else:
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if user is None:
            return render(
                request,
                "signin.html",
                {
                    "form": AuthenticationForm,
                    "error": "El nombre de usuario o contraseña es incorrecto",
                },
            )
        else:
            login(request, user)
            messages.add_message(request, messages.INFO, "Inicio de sesión correcto")
            return redirect("tasks")


def error_404_view(request, exception):
    return render(request, "404.html")


def error_500_view(request, exception):
    return render(request, "500.html")
