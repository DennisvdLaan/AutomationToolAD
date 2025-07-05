# main/task_manager.py

import logging

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.results = {}
        self.logger = logging.getLogger()

    def add_task(self, name, function, *args, **kwargs):
        """
        Voeg een taak toe aan de wachtrij.
        :param name: Naam van de taak (string)
        :param function: Functie die uitgevoerd moet worden
        :param args: Positional arguments voor de functie
        :param kwargs: Keyword arguments voor de functie
        """
        self.tasks.append((name, function, args, kwargs))
        self.logger.debug(f"📌 Taak toegevoegd: {name}")

    def run_all(self):
        """
        Voert alle toegevoegde taken uit en slaat de resultaten op.
        """
        self.logger.info(f"🚀 Start met uitvoeren van {len(self.tasks)} taken...")
        for name, func, args, kwargs in self.tasks:
            try:
                self.logger.info(f"▶️  Uitvoeren taak: {name}")
                result = func(*args, **kwargs)
                self.results[name] = result
                self.logger.info(f"✅  Taak voltooid: {name}")
            except Exception as e:
                self.logger.error(f"❌  Fout bij uitvoeren van taak '{name}': {e}")
                self.results[name] = {"error": str(e)}

    def get_results(self):
        """
        Retourneert alle verzamelde resultaten.
        """
        return self.results
