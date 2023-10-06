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
    
    @classmethod
    def from_oink(cls, typ, size, max_param, deg, inst):
        f=open("oink_results/" + typ + "/" + "size" + str(size) + "max" + str(max_param) + "deg" + str(deg) + "/" + "{:04d}".format(inst), "r")
        lines = f.readlines()
        f.close()
        is_timeout = (lines[6][11:21] == "terminated")
        infos = {}
        if(not(is_timeout)):
            infos["iterations"] = int(lines[6][23:-13])
            infos["runtime"] = float(lines[8][24:-5])
        else:
            infos["iterations"] = 0
            infos["runtime"] = float(lines[6][2:6])
        return(transcript(size, max_param, deg, 0, is_timeout, infos))

    