from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import random
import markdown2

from . import util


def index(request):
    # GET QUERY
    entries = []
    page_title = "All Pages"
    query = request.GET.get('q', '')

    # IF NO QUERYSTRING
    if query == None or len(query) < 1:
        entries = util.list_entries()
    
    # IF THERE IS QUERYSTRING
    else:
        # SEARCH ENTRY WITH QUERYSTRING
        entry = util.get_entry(query)

        # IF THERE IS ENTRY WITH QUERYSTRING
        if entry != None:
            print(entry)
            return HttpResponseRedirect(f"./{query}")
        # IF THERE IS NO ENTRY WITH QUERYSTRING
        else:
            entries = util.search_entries(query)
            if entries == None or len(entries) < 1:
                entries = util.list_entries()
            else:
                page_title = "Search results"
    return render(request, "encyclopedia/index.html", {
        "entries": entries,
        "page_title": page_title
    })

def entry(request, title):
    entry = util.get_entry(title)

    # IF ENTRY NOT EXIST
    if entry == None:
        return render(request, "encyclopedia/404.html")
    
    # IF ENTRY EXIST
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry": markdown2.markdown(entry)
    })

def new_entry(request):
    message = None
    if request.method == "POST":
        title = request.POST.get('title', '')
        text = request.POST.get('entry', '')

        if title == None or len(title) < 1 or text == None or len(text) < 1:
            # NO TITLE OR TEXT
            message = "no title or content"
        else:
            # IF title ALREADY EXISTS
            exist_entry = util.get_entry(title)
            if exist_entry != None:
                message = f"{title} is already exist!"
            else:
                print("title", title, "content", text)
                op = util.save_entry(title, text)
                print("op: ", op)
                if op != 0:
                    message = "Error while entry saving!"
                else:
                    return HttpResponseRedirect(f"./{title}")
    return render(request, "encyclopedia/new_entry.html", { "message": message, "title": "New Entry", "action": "./new-entry"})

def edit_entry(request):
    message = ""
    title = "Editing"
    edit_content = None
    if request.method == "POST":
        edit_title = request.POST.get('title', '')
        edit_content = request.POST.get('entry', '')
        print("edit_title", edit_title, "edit entry", edit_content)
        if edit_title == None or len(edit_title) < 1 or util.get_entry(edit_title) == None:
            # NO TITLE
            return HttpResponseRedirect("./")
        else:
            if edit_content == None or len(edit_content) < 1:
                # THERE IS NO CONTENT
                message = "no content"
            else:
                # THERE IS TITLE AND CONTENT
                act = util.save_entry(edit_title, edit_content)
                if act == 0:
                    return HttpResponseRedirect(f"./{edit_title}")
                else:
                    message = "error while updating content"
    else:
        edit_title = request.GET.get('q', '')
        if edit_title == None or len(edit_title) < 1:
            # NO QUERYSTRING
            return HttpResponseRedirect("./")
        else:
            exist_enty = util.get_entry(edit_title)
            if exist_enty == None:
                # NO ENTRY
                return HttpResponseRedirect("./")
            else:
                # ENTRY FOUND
                edit_content = exist_enty

    return render(request, "encyclopedia/new_entry.html", 
                  { 
                    "message": message, "title": title,
                    "action": "./edit-entry", 
                    "disable": "readonly",
                    "edit_title": edit_title,
                    "edit_content": edit_content
                }
            )

def get_random(request):
    random_title = "CSS"
    # TAKE LIST
    lists = util.list_entries()
    number_of_lists = len(lists)
    # GET A RANDOM INDEX NUMBER BETWEEN 0 AND LENGTH OF LIST
    random_number = random.randint(0, number_of_lists - 1)
    random_title = lists[random_number]

    return HttpResponseRedirect(f"./{random_title}")
