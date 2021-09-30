"""
Some example strategies for people who want to create a custom, homemade bot.
And some handy classes to extend
"""

import chess
from chess.engine import PlayResult
import random
from engine_wrapper import EngineWrapper


class FillerEngine:
    """
    Not meant to be an actual engine.

    This is only used to provide the property "self.engine"
    in "MinimalEngine" which extends "EngineWrapper"
    """
    def __init__(self, main_engine, name=None):
        self.id = {
            "name": name
        }
        self.name = name
        self.main_engine = main_engine

    def __getattr__(self, method_name):
        main_engine = self.main_engine

        def method(*args, **kwargs):
            nonlocal main_engine
            nonlocal method_name
            return main_engine.notify(method_name, *args, **kwargs)

        return method


"""class ExampleEngine(MinimalEngine):
    pass


# Strategy names and ideas from tom7's excellent eloWorld video

class RandomMove(ExampleEngine):
    def search(self, board, *args):
        return PlayResult(random.choice(list(board.legal_moves)), None)"""


class MinimalEngine(EngineWrapper):
    """
    Subclass this to prevent a few random errors

    Even though MinimalEngine extends EngineWrapper,
    you don't have to actually wrap an engine.

    At minimum, just implement `search`,
    however you can also change other methods like
    `notify`, `first_search`, `get_time_control`, etc.
    """
    def __init__(self, *args, name=None):
        super().__init__(*args)

        self.engine_name = self.__class__.__name__ if name is None else name

        self.last_move_info = []
        self.engine = FillerEngine(self, name=self.name)
        self.engine.id = {
            "name": self.engine_name
        }

    def search_with_ponder(self, board, wtime, btime, winc, binc, ponder, draw_offered):
        timeleft = 0
        if board.turn:
            timeleft = wtime
        else:
            timeleft = btime
        return self.search(board, timeleft, ponder, draw_offered)

    def search(self, board, timeleft, ponder, draw_offered):
        """
        The method to be implemented in your homemade engine

        NOTE: This method must return an instance of "chess.engine.PlayResult"
        """
        raise NotImplementedError("The search method is not implemented")

    def notify(self, method_name, *args, **kwargs):
        """
        The EngineWrapper class sometimes calls methods on "self.engine".
        "self.engine" is a filler property that notifies <self> 
        whenever an attribute is called.

        Nothing happens unless the main engine does something.

        Simply put, the following code is equivalent
        self.engine.<method_name>(<*args>, <**kwargs>)
        self.notify(<method_name>, <*args>, <**kwargs>)
        """
        pass


class Minimax(MinimalEngine): 
    
    def search(self, board, timeleft, *otros):

        arbol = Arbol(board, 3)

        print("nodos visitados: " + str(arbol.nodos_totales))
        print("evaluacion: " + str(arbol.raiz.evaluacion))

        return PlayResult(arbol.raiz.mejor_movida, None)

class Arbol():

    def __init__(self, posicion_inicial, profundidad):
        self.prof_max = profundidad
        self.prof_vista = 0
        self.raiz = Nodo(posicion_inicial)
        self.nodos_totales = 1

        #self.expandir_recursivo(self.raiz, 0)
        print("----- genrando arbol -----")
        self.generar_arbol()
        print("----- minimax -----")
        self.minimax(self.raiz)

    #GENERAR ARBOL EN BASE A NODOS VISITADOS
    def generar_arbol(self):
        while self.prof_vista <= self.prof_max:
            self.expandir_capa(self.raiz)
            self.prof_vista += 1

    def expandir_capa(self, nodo_actual):
        if len(nodo_actual.hijos()) == 0:
            nodo_actual.generar_hijos()
            self.nodos_totales += len(nodo_actual.hijos())
            return
        for hijo in nodo_actual.hijos():
            self.expandir_capa(hijo)

    def expandir_recursivo(self, nodo_actual, prof_actual):
        if prof_actual > self.prof_max:
            return

        nodo_actual.generar_hijos()
        for i in nodo_actual.hijos():
            self.expandir_recursivo(i, prof_actual + 1)
        self.nodos_totales += len(nodo_actual.hijos())

    def minimax(self, nodo_actual): #hacerlo con profundidad

        if (len(nodo_actual.hijos()) == 0) or (nodo_actual.terminada):
            return nodo_actual.evaluar()

        if nodo_actual.turno_blancas:
            mejor_eval = -100000
            for hijo in nodo_actual.hijos():
                evaluacion = self.minimax(hijo)
                #print("hoja eval " + str(evaluacion))
                if evaluacion > mejor_eval:
                    mejor_eval = evaluacion
                    mejor_movida = hijo.board.peek()
                if evaluacion == 1000: 
                    break
        else:
            mejor_eval = 100000
            for hijo in nodo_actual.hijos():
                evaluacion = self.minimax(hijo)
                if evaluacion < mejor_eval:
                    mejor_eval = evaluacion
                    mejor_movida = hijo.board.peek()
                if evaluacion == -1000: 
                    break
        nodo_actual.evaluacion = mejor_eval
        nodo_actual.mejor_movida = mejor_movida
        return mejor_eval

        #la versiona anterior
        """
        for hijo in nodo_actual.hijos():
            self.minimax(hijo)

        mejor_movida = False
        if nodo_actual.turno_blancas:
            mejor_eval = -100000
            for i in nodo_actual.hijos():
                if i.evaluacion > mejor_eval:
                    mejor_eval = i.evaluacion
                    mejor_movida = i.board.peek()
                if i.evaluacion == -1000: 
                    break;
        else:
            mejor_eval = 100000
            for i in nodo_actual.hijos():
                if i.evaluacion <= mejor_eval:
                    mejor_eval = i.evaluacion
                    mejor_movida = i.board.peek()
                if i.evaluacion == -1000: 
                    break;
        nodo_actual.evaluacion = mejor_eval
        nodo_actual.mejor_movida = mejor_movida"""

        """print("mejor eval blancas " + str(nodo_actual.turno_blancas) + str(mejor_eval))"""


class Nodo():
    def __init__(self, board):
        self.board = board
        self.nodos_hijos = []
        self.turno_blancas = (board.turn == chess.WHITE)
        outcome = self.board.outcome()
        self.terminada = not (outcome == None)
        if(self.terminada):
            self.gano_blancas = bool(outcome.winner == chess.WHITE)
        self.evaluacion = False
        self.mejor_movida = False

    def hijos(self):
        return self.nodos_hijos

    def generar_hijos(self):
        movidas = list(self.board.legal_moves)
        for i in movidas:
            nuevo_board = self.board.copy()
            nuevo_board.push(i)
            nuevo_nodo = Nodo(nuevo_board)
            self.nodos_hijos.append(nuevo_nodo)

    def evaluar(self):
        eval_negras = 0
        eval_blancas = 0
        material = 0
        #jaque mate
        if self.terminada:
            if self.gano_blancas:
                eval_blancas = 1000
            else:
                eval_negras = 1000
        else: 
            #material
            #print(self.board.board_fen())
            material = self.contar_material(self.board.board_fen())

            #enroque
            """if self.board.has_castling_rights(chess.WHITE):
                eval_blancas += 0.5
            if self.board.has_castling_rights(chess.BLACK):
                eval_negras += 0.5"""
        self.evaluacion = material + eval_blancas - eval_negras
        return self.evaluacion

    def contar_material(self, fen):
        material = 0
        valores_piezas = {"p": -1, "n": -3, "b": -3, "r": -5, "q": -9, "P": 1, "N": 3, "B": 3, "R": 5, "Q": 9}
        for i in fen:
            if i in valores_piezas:
                material += valores_piezas[i]
        return material