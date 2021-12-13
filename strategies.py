"""
Some example strategies for people who want to create a custom, homemade bot.
And some handy classes to extend
"""

import chess
from chess.engine import PlayResult
import random
from engine_wrapper import EngineWrapper
import math

Infinity = 100000

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

        #ERROR SI EMPIEZA DSDE OTRA POS
        #self.arbol = Arbol(chess.Board(chess.STARTING_FEN), 2)

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
        
        #falla si arracna el bot
        #self.arbol.actualizar_raiz(board.peek())

        self.arbol = Arbol(board, 3)

        self.arbol.buscar(3)
        print("nodos totales: " + str(self.arbol.nodos_totales))
        print("nodos evaluados: " + str(self.arbol.nodos_evaluados))
        print("Profundidad: " + str(self.arbol.profundidad))
        print("evaluacion: " + str(self.arbol.raiz.evaluacion))

        mejor_mov = self.arbol.raiz.mejor_movida
        #self.arbol.actualizar_raiz(mejor_mov)
        return PlayResult(mejor_mov, None)
        #return PlayResult(random.choice(list(board.legal_moves)), None)

class Arbol():

    def __init__(self, posicion_inicial, prof_inicial):
        
        print("genrando arbol")
        self.nodos_totales = 1
        self.nodos_evaluados = 0
        self.profundidad = 0
        self.raiz = Nodo(posicion_inicial, None)
        """if posicion_inicial.ply() > 0:
            self.raiz = Nodo(posicion_inicial, posicion_inicial.peek())
        else:"""
        self.expandir_niveles(prof_inicial)
        

    #GENERAR ARBOL EN BASE A NODOS VISITADOS
    def expandir_niveles(self, niveles_a_agregar):
        for i in range(niveles_a_agregar):
            self.expandir_un_nivel(self.raiz)
            self.profundidad += 1

    def expandir_un_nivel(self, nodo_actual):
        if len(nodo_actual.hijos()) == 0:
            nodo_actual.generar_hijos()
            self.nodos_totales += len(nodo_actual.hijos())
            return
        for hijo in nodo_actual.hijos():
            self.expandir_un_nivel(hijo)

    def actualizar_raiz(self, ultima_movida):
        for hijo in self.raiz.hijos():
            if hijo.ult_movida == ultima_movida:
                self.raiz = hijo
                self.profundidad -= 1
                print("Nueva raiz: " + hijo.ult_movida.uci())
                return

    def buscar(self, profundidad):
        print("buscando")

        if self.profundidad < profundidad:
            self.expandir_niveles(profundidad - self.profundidad)

        self.minimax(self.raiz, profundidad, -Infinity, Infinity)

    """def expandir_recursivo(self, nodo_actual, prof_actual):
        if prof_actual > self.prof_max:
            return

        nodo_actual.generar_hijos()
        for i in nodo_actual.hijos():
            self.expandir_recursivo(i, prof_actual + 1)
        self.nodos_totales += len(nodo_actual.hijos())"""

    def minimax(self, nodo_actual, prof, alpha, beta): #hacerlo con profundidad

        if prof == 0 or (len(nodo_actual.hijos()) == 0) or (nodo_actual.terminada):
            self.nodos_evaluados += 1
            return nodo_actual.evaluar()

        #MAXIMIZER
        if nodo_actual.turno_blancas:
            mejor_eval = -Infinity
            for hijo in nodo_actual.hijos(): 
                evaluacion = self.minimax(hijo, prof -1, alpha, beta)
                if evaluacion > mejor_eval:
                    mejor_eval = evaluacion
                    mejor_movida = hijo.ult_movida
                if mejor_eval > alpha:
                    alpha = mejor_eval
                if beta <= alpha or mejor_eval > 950: 
                    break
        else: #MINIMIZER
            mejor_eval = Infinity
            for hijo in nodo_actual.hijos():
                evaluacion = self.minimax(hijo, prof -1, alpha, beta)
                if evaluacion < mejor_eval:
                    mejor_eval = evaluacion
                    mejor_movida = hijo.ult_movida
                if beta <= alpha or mejor_eval < -950:
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
    def __init__(self, board, movida):
        self.board = board
        self.ult_movida = movida
        self.nodos_hijos = []
        self.turno_blancas = (board.turn == chess.WHITE)
        outcome = self.board.outcome()
        self.terminada = not (outcome == None)
        if(self.terminada):
            self.gano_blancas = bool(outcome.winner == chess.WHITE)
            self.gano_negras = bool(outcome.winner == chess.BLACK)
        self.evaluacion = False
        self.mejor_movida = False

    def hijos(self):
        return self.nodos_hijos

    def generar_hijos(self):
        movidas = list(self.board.legal_moves)
        capturas = [] 
        jaques = []
        normales = []
        for mov in movidas:
            nuevo_board = self.board.copy()
            nuevo_board.push(mov)
            nuevo_nodo = Nodo(nuevo_board, mov)
            if nuevo_board.is_check():
                jaques.append(nuevo_nodo)
            elif self.board.is_capture(mov):
                #print("is capture" + str(mov))
                capturas.append(nuevo_nodo)
            else:
                normales.append(nuevo_nodo)
        self.nodos_hijos = jaques + capturas + normales

    def evaluar(self):
        evaluacion = 0
        #jaque mate
        if self.terminada:
            if self.gano_blancas:
                evaluacion = 1000
            elif self.gano_negras:
                evaluacion = -1000
            else:
                evaluacion = 0
        else: 
            #material
            #evaluacion += self.contar_material(self.board.board_fen())

            
            if self.turno_blancas:
                #movidas
                movidas_blancas = self.board.legal_moves.count()
                tablero_turno_cambiado = self.board.copy()
                tablero_turno_cambiado.push(chess.Move.null())
                movidas_negras = tablero_turno_cambiado.legal_moves.count()
                #enroque
                #if self.board.is_castling()
            else:
                #movidas
                movidas_negras = self.board.legal_moves.count()
                tablero_turno_cambiado = self.board.copy()
                tablero_turno_cambiado.push(chess.Move.null())
                movidas_blancas = tablero_turno_cambiado.legal_moves.count()
            #evaluacion += math.tanh((movidas_blancas - movidas_negras) * 0.2)*0.5
            #evaluacion += (((movidas_blancas - movidas_negras)+20)/(40))*0.5
                
            #enroque
            """if self.board.has_castling_rights(chess.WHITE):
                eval_blancas += 0.5
            if self.board.has_castling_rights(chess.BLACK):
                eval_negras += 0.5"""   
        self.evaluacion = evaluacion
        return self.evaluacion

    def contar_material(self, fen):
        material = 0
        valores_piezas = {"p": -1, "n": -3, "b": -3.1, "r": -5, "q": -9, "P": 1, "N": 3, "B": 3.1, "R": 5, "Q": 9}
        for i in fen:
            if i in valores_piezas:
                material += valores_piezas[i]
        return material