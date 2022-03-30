class DisabledTracker(object):
    """Bugtracker which is currently disabled."""

    url = None

    def __init__(self, projects):
        self.projects = projects

    def update_entry(self, entry):
        pass

    def get_subject(self, issue_id):
        return None
