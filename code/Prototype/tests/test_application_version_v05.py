"""Active checkout identity from synthetic repositories, never shell cwd."""
from pathlib import Path
import subprocess

from dvk.application_version import active_application_version


def git(root,*args):
    return subprocess.run(['git','-C',str(root),*args],check=True,capture_output=True,text=True).stdout.strip()


def repository(tmp_path):
    root = tmp_path/'repo'
    root.mkdir()
    git(root,'init','-b','synthetic-base')
    git(root,'config','user.name','Synthetic')
    git(root,'config','user.email','synthetic@example.invalid')
    app = root/'code'/'streamlit_app.py'
    app.parent.mkdir()
    app.write_text('# synthetic application\n')
    git(root,'add','.')
    git(root,'commit','-m','Synthetic baseline')
    return root,app


def test_working_directory_cannot_change_identity_and_worktrees_differ(tmp_path,monkeypatch):
    root,app = repository(tmp_path)
    worktree = tmp_path/'other-worktree'
    git(root,'worktree','add','-b','synthetic-work',str(worktree))
    monkeypatch.chdir(worktree)
    version = active_application_version(app)
    assert 'synthetic-base' in version and str(root) in version
    assert git(root,'rev-parse','--short=12','HEAD') in version
    assert 'lokale wijzigingen' not in version
    other_app = worktree/'code'/'streamlit_app.py'
    assert 'synthetic-work' in active_application_version(other_app)
    assert str(worktree) in active_application_version(other_app)
    other_app.write_text('# changed synthetic application\n')
    assert 'lokale wijzigingen' in active_application_version(other_app)
    assert 'lokale wijzigingen' not in active_application_version(app)
    git(worktree,'add','.')
    assert 'lokale wijzigingen' in active_application_version(other_app)
    git(worktree,'commit','-m','Synthetic change')
    assert git(worktree,'rev-parse','--short=12','HEAD') in active_application_version(other_app)
    assert 'lokale wijzigingen' not in active_application_version(other_app)
    (root/'new.py').write_text('# untracked source\n')
    assert 'lokale wijzigingen' in active_application_version(app)


def test_missing_git_or_untracked_application_is_honest(tmp_path,monkeypatch):
    app = tmp_path/'app.py'
    app.write_text('# synthetic\n')
    assert 'niet beschikbaar' in active_application_version(app)
    root,tracked = repository(tmp_path)
    other = root/'other.py'
    other.write_text('# synthetic\n')
    assert 'niet beschikbaar' in active_application_version(other)
    monkeypatch.setenv('PATH','')
    assert 'niet beschikbaar' in active_application_version(tracked)


def test_caption_immediately_below_exact_title(tmp_path):
    from streamlit.testing.v1 import AppTest
    source = Path(__file__).parents[1]/'streamlit_app.py'
    script = tmp_path/'streamlit_app.py'
    script.write_text(source.read_text())
    app = AppTest.from_file(str(script),default_timeout=20).run()
    assert not app.exception
    nodes = list(app.main)
    title_index = next(i for i,n in enumerate(nodes) if n.type=='title')
    assert nodes[title_index].value == 'CKC Digitaal Verenigingskantoor (DVK)'
    assert nodes[title_index+1].type == 'caption'
    assert 'versie-informatie niet beschikbaar' in nodes[title_index+1].value
