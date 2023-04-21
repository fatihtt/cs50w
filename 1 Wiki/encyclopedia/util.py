import re
import fnmatch
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))

def search_entries(q):
    _, filenames = default_storage.listdir("entries")
    print("file names : ", filenames)
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if fnmatch.fnmatch(filename.lower(), f"*{q.lower()}*")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    try:
        filename = f"entries/{title}.md"
        if default_storage.exists(filename):
            default_storage.delete(filename)
        default_storage.save(filename, ContentFile(content))
        return 0
    except Exception as e:
        return 1


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None
