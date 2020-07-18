import numpy as np

class abstract_graph:
    
    def __init__(self,_edges):
        self.edges=_edges
        self.nodes={u for u,v in self.edges} | {v for u,v in self.edges}
        
    def adjacency_matrix(self):
        pass
    
    def adjacency_list(self):
        pass


class simple_graph(abstract_graph):
    
    def __init__(self,_edges):
        tmp=[]
        for (u,v) in _edges:
            if (v,u) not in tmp and v!=u:
                tmp.append((u,v))
        self.edges=tmp
        self.nodes={u for u,v in _edges} | {v for u,v in _edges}
     
    def adjacency_matrix(self):
        # completar
        n=len(self.nodes)
        mat=np.zeros((n,n))
        for i,v in enumerate(self.nodes):
            for j,k in enumerate(self.nodes):
                if (v,k) in self.edges:
                    mat[i,j]=1
                    mat[j,i]=1
        return mat
    
    
    def adjacency_list(self):
        adjacent=lambda n : {v for u,v in self.edges if u==n } | {u for u,v in self.edges if v==n}
        return {v:adjacent(v) for v in self.nodes}
        
E=[('A','B'),('C','D'),('B','D'),('B','A'),('A','A')]
G=simple_graph(E)
print('aristas',G.edges)
print('nodos : ',G.nodes)
print('matriz adyacencia : ',G.adjacency_matrix())
print('lista adyacencia : ',G.adjacency_list())


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


class digraph(abstract_graph):
    
    def __init__(self,_edges):
        tmp=[]
        for (u,v) in _edges:
            if (v,u) not in tmp:
                tmp.append((u,v))
        self.edges=tmp
        self.nodes={u for u,v in self.edges} | {u for u,v in self.edges}

        
    def adjacency_matrix(self):
        # completar
        pass
    
    def adjacency_list(self):
        # completar
        pass
    

E3=[(1,2),(3,4),(2,4),(2,1),(2,1)]
G3=digraph(E3)
print('nodos : ',G3.nodes)
print('aristas : ',G3.edges)
print('lista adyacencia : ',G3.adjacency_list())


class weighted_graph(abstract_graph):
    
    def __init__(self,_edges):
        self.edges=_edges
        self.nodes={u for u,v in self.edges.keys()} | {v for u,v in self.edges.keys()}
        
    def adjacency_matrix(self):
        # completar
        n=len(self.nodes)
        mat=np.zeros((n,n))
        return mat
    
    def adjacency_list(self):
        adjacent=lambda n : {v for u,v in self.edges.keys() if u==n } | {u for u,v in self.edges.keys() if v==n}
        return {v:adjacent(v) for v in self.nodes}

E4={(1,2):1,(3,4):2,(2,4):1}
G4=weighted_graph(E4)
print('nodos : ',G4.nodes)
print(G4.adjacency_matrix())
print('lista adyacencia : ',G4.adjacency_list())
