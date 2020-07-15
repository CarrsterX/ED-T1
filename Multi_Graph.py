import numpy as np

class multi_graph(abstract_graph):
    

    def adjacency_matrix(self):
        # completar
        pass
    
    def adjacency_list(self):
        # completar
        pass
    
E2=[(1,2),(3,4),(2,4),(1,2),(1,1)]
G2=multi_graph(E2)
print('nodos : ',G2.nodes)
print('aristas : ',G2.edges)
print('matriz adyacencia : ',G2.adjacency_matrix())
print('lista adyacencia : ',G2.adjacency_list())