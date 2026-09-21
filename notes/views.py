from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import NoteForm
from .models import Note, NoteFolder


@login_required
def note_list(request):
    folder_id = request.GET.get("folder")
    search = request.GET.get("q")
    notes = Note.objects.filter(user=request.user)
    if folder_id:
        notes = notes.filter(folder_id=folder_id)
    if search:
        notes = notes.filter(title__icontains=search)

    folders = NoteFolder.objects.filter(user=request.user)
    return render(request, "notes/list.html", {"notes": notes, "folders": folders, "active_folder": folder_id})


@login_required
def note_edit(request, pk=None):
    note = get_object_or_404(Note, pk=pk, user=request.user) if pk else None
    if request.method == "POST":
        form = NoteForm(request.POST, instance=note, user=request.user)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, "Note saved.")
            return redirect("notes:edit", pk=note.pk)
    else:
        form = NoteForm(instance=note, user=request.user)
    return render(request, "notes/editor.html", {"form": form, "note": note})


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == "POST":
        note.delete()
        messages.success(request, "Note deleted.")
        return redirect("notes:list")
    return render(request, "notes/confirm_delete.html", {"note": note})
