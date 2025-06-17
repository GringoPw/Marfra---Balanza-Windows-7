from datetime import datetime
from typing import List, Optional

class Fardo:
    """Modelo para representar un fardo"""
    
    def __init__(self, numero: int, peso: float):
        self.numero = numero
        self.peso = peso
        self.hora_pesaje = datetime.now()
    
    def __str__(self):
        return f"Fardo #{self.numero}: {self.peso:.2f} kg"

class Ticket:
    """Modelo para representar un ticket de pesaje"""
    
    def __init__(self, numero: str):
        self.numero = numero
        self.fecha_creacion = datetime.now()
        self.fardos: List[Fardo] = []
        self.observaciones: str = ""
        self.kg_bruto_romaneo: Optional[float] = None
        self.agregado: float = 0.0
        self.resto: float = 0.0
        self.rinde: Optional[float] = None
    
    def agregar_fardo(self, fardo: Fardo) -> None:
        """Agrega un fardo al ticket"""
        # Verificar que no exista un fardo con el mismo número
        for f in self.fardos:
            if f.numero == fardo.numero:
                raise ValueError(f"Ya existe un fardo con el número {fardo.numero}")
        
        self.fardos.append(fardo)
    
    def eliminar_fardo(self, numero_fardo: int) -> None:
        """Elimina un fardo del ticket por su número"""
        for i, fardo in enumerate(self.fardos):
            if fardo.numero == numero_fardo:
                self.fardos.pop(i)
                return
        
        raise ValueError(f"No se encontró un fardo con el número {numero_fardo}")
    
    def obtener_peso_total(self) -> float:
        """Calcula el peso total de todos los fardos"""
        return sum(fardo.peso for fardo in self.fardos)
        
    def calcular_rinde(self, kg_bruto_romaneo: float, agregado: float, resto: float) -> float:
        """Calcula el rinde según la fórmula: (kg total fardos + resto - agregado - tara)/Kgbrutos romaneo * 100"""
        if not kg_bruto_romaneo or kg_bruto_romaneo <= 0:
            return 0.0
            
        peso_total = self.obtener_peso_total()
        tara = len(self.fardos) * 2  # 2kg por fardo
        
        return ((peso_total + resto - agregado - tara) / kg_bruto_romaneo) * 100
    
    def obtener_cantidad_fardos(self) -> int:
        """Obtiene la cantidad de fardos en el ticket"""
        return len(self.fardos)
    
    def __str__(self):
        return f"Ticket #{self.numero}: {self.obtener_cantidad_fardos()} fardos, {self.obtener_peso_total():.2f} kg"
