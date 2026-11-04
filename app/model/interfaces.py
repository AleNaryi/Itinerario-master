from abc import ABC, abstractmethod


class CrudInterface(ABC):

    @abstractmethod
    def confirmar_registro(self):
        pass

    @abstractmethod
    def confirmar_modificacion(self, id):
        pass

    @abstractmethod
    def confirmar_eliminacion(self, id):
        pass

    @abstractmethod
    def consultar(self):
        pass
