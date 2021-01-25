import ast

class transcript:
    '''
    stores informations regarding an execution
    '''
    
    def __init__(self, size, max_param, deg, timeout, is_timeout, infos):
        self.size = size
        self.max_param = max_param
        self.deg = deg
        self.timeout = timeout
        self.is_timeout = is_timeout
        self.infos = infos
        
    @classmethod
    def from_file(cls, typ, alg, size, max_param, deg, inst):
        f = open("executions/" + typ + "/" + alg + "/size" + str(size) + "max" + str(max_param) + "deg" + str(deg) + "/" + "{:04d}".format(inst), "r")
        lines = f.readlines()
        f.close()
        timeout = int(lines[0][9:-1])
        is_timeout = {"True":True, "False":False}[lines[1][12:-1]]
        infos = ast.literal_eval(lines[3][7:])
        return(transcript(size, max_param, deg, timeout, is_timeout,infos))
    
    