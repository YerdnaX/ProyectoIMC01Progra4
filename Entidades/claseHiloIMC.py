import threading
import time
from queue import Queue
from typing import Callable, Optional


class HiloIMC(threading.Thread):
    def __init__(
        self,
        indices_segmento,
        log_queue: Queue,
        lista_personas,
        calcular_imc_fn: Callable[[float, float], float],
        estado_imc_fn: Callable[[str, int, float, float, str, float], str],
        lock: Optional[threading.Lock] = None,
        nombre: str = "",
    ):
        super().__init__(name=nombre or None, daemon=True)
        self.indices_segmento = list(indices_segmento)
        self.log_queue = log_queue
        self.lista_personas = lista_personas
        self.calcular_imc_fn = calcular_imc_fn
        self.estado_imc_fn = estado_imc_fn
        self.lock = lock

    def run(self):
        self.log_queue.put(f"{self.name} inicia (registros {len(self.indices_segmento)}).")
        for indices in self.indices_segmento:
            try:
                persona = self.lista_personas[indices]
            except Exception:
                continue
            imc = self.calcular_imc_fn(persona.peso, persona.estatura)
            estado = self.estado_imc_fn(persona.genero, persona.edad, persona.estatura, persona.peso, persona.genero, imc)
            if self.lock:
                with self.lock:
                    persona.imcCalculado = imc
                    persona.estado = estado
            else:
                persona.imcCalculado = imc
                persona.estado = estado
            self.log_queue.put(f"{self.name} procesó ID {persona.id} -> IMC {imc:.2f}, {estado}")
            ## Pa ceder CPU para que otros hilos también avancen y los logs se intercalen
            time.sleep(1)
        self.log_queue.put(f"{self.name} termina.")
