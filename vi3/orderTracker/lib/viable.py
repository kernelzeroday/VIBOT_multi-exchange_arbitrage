debug=True
def viable(mode,orig,new):
    if debug: print("[i] DEBUG: " +str(mode) + " " + str(orig)+ " " +str(new))
    if mode == 'sell':
        decrease = float(orig) - float(new)
        pct = float(decrease) / float(orig) * float(100.00)
        if float(pct) <= 0.125 and float(pct) > 0.0 :
           if debug: print('[i] : Viable:' + str(pct))
           return True
        else:
           if debug:print("[i] Pct was: " +str(pct))
           return False
    elif mode == 'buy':
        increase = float(new) - float(orig)
        pct = float(increase) / float(orig) * float(100)
        if float(pct) <= 0.125 and float(pct) > 0.0:
            if debug: print('[i] : Viable: ' + str(pct))
            return True
        else:
            if debug:print("[i] Pct was: " +str(pct))
            return False
    else:
       logger.info('Error: Invalid mode.')
       return False

