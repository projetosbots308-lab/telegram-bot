# utils/loader.py

import os
import importlib
import inspect

SOURCES_FOLDER = "sources"


def get_all_sources():
    sources = {}

    for file in os.listdir(SOURCES_FOLDER):

        if file.endswith(".py") and not file.startswith("_"):

            module_name = file[:-3]

            try:
                module = importlib.import_module(f"{SOURCES_FOLDER}.{module_name}")

                for name, obj in inspect.getmembers(module):

                    if inspect.isclass(obj):

                        try:
                            instance = obj()

                            # verifica se tem métodos obrigatórios
                            if all(hasattr(instance, m) for m in ["search", "chapters", "pages"]):

                                sources[name] = instance
                                print(f"✔ Fonte carregada: {name}")

                        except Exception as e:
                            print(f"Erro ao iniciar fonte {name}: {e}")

            except Exception as e:
                print(f"Erro ao importar {module_name}: {e}")

    print(f"📚 Total de fontes carregadas: {len(sources)}")

    return sources
