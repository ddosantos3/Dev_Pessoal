from __future__ import annotations
from pathlib import Path

from git import Repo
from git.exc import BadName


class GitClient:
    def __init__(self, repo_dir: str):
        self.repo_path = Path(repo_dir)
        if (self.repo_path / ".git").exists():
            self.repo = Repo(self.repo_path)
        else:
            self.repo = Repo.init(self.repo_path)

    def commit_tudo(self, mensagem: str) -> str:
        repo = self.repo
        repo.git.add(all=True)

        try:
            head_valido = repo.head.is_valid()
        except (TypeError, ValueError, BadName):
            head_valido = False

        if not head_valido or repo.is_dirty(index=True, working_tree=False, untracked_files=False):
            commit = repo.index.commit(mensagem)
            return commit.hexsha

        return repo.head.commit.hexsha
