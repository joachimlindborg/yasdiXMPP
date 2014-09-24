about = """
Titel: pyYASDI
Autor: Sebastian Schulte
Version: 1.0.0
Datum: 18.3.07 / 18.3.07 / 18.3.07
Datei: pyYASDI.py

+ SMA YASDI Library Wrapper fuer Python Scripting Language v1"""
import yasdiwrapper

class pyYASDI:
    """pyYASDI - ermoeglicht bequeme SMANet bedienung"""
    def __init__(self,driver=0,debug=0,max_devices=1):
        """Konstruktor
                Parameter:
                driver = 0          0 = 1.Driver in der yasdi.ini
                debug = 1/0         1 = an oder 0 = aus
                max_devices = 1     maximale Geraete die zu suchen sind"""
        self.max_devices = max_devices
        self.debug = debug
        self.driver = driver
        self.DeviceList = []
        self.YasdiMaster = yasdiwrapper.YasdiMaster()
        self.Yasdi = yasdiwrapper.Yasdi()
        self.YasdiMaster.yasdiMasterInitialize()
        
        self.DriverName = self.goOnline(self.driver)
        if self.DriverName == 0: self.die()
        
        result = self.detectDevices(self.max_devices)

        self.load_devices()

    def msg(self,msg,error=0):
        """msg Methode fuer Debug ausgaben etc.
                Parameter:
                msg =               Die Nachricht die ausgegeben / gespeichert werden soll
                error = 0           error = 0 Status error = 1 Fehlermeldung"""
        if error == 0: 
            if self.debug: print ":>        %s"%(msg)
        elif error == 1:
            if self.debug: print ":> Error: %s"%(msg)

    def quit(self):
        """Beendet den Yasdi-Master und gibt die Resourcen wieder frei"""
        self.YasdiMaster.yasdiMasterShutdown()

    def die(self):
        """Beendet den Yasdi-Master aufgrund eines Fehlers"""
        self.msg("gestorben",1)
        self.quit()

    def goOnline(self,driver):
        """Sorgt dafuer das eine Schnittstelle eingeschaltet wird
                Parameter:
                driver              0 = 1. Schnittstelle in yasdi.ini usw.
                Ergebnis:
                0                   bei Fehler oder z.B.
                COM1                Wenn die erste serielle Schnittstelle geladen wurde"""
        anzdriver = self.Yasdi.yasdiGetDriver()
        if anzdriver == 0:
            self.msg("konnte Schnittstelle nicht laden",1)
            return anzdriver
        else:
            self.Yasdi.yasdiSetDriverOnline(driver)
            DriverName = self.Yasdi.yasdiGetDriverName(driver)
            self.msg("Schnittstelle %s bereit"%(DriverName))
            return DriverName

    def detectDevices(self,max_devices):
        """Geraeteerkennung
                Parameter:
                max_devices         max. Geraete die gesucht werden sollen
                Ergebnis:
                0                   wenn nicht alle Geraete gefunden wurden
                1                   wenn alle Geraete gefunden wurden"""
        result = self.YasdiMaster.DoMasterCmdEx(max_devices)
        if result == -1:
            self.msg("konnte nicht alle %s Geraete finden"%(self.max_devices),1)
            return 0
        elif not result:
            self.msg("konnte alle Geraete finden",0)
            return 1

    def get_masterstatus(self):
        """Gibt den Status des Masters zurueck, per return und print
                Ergebnis:
                1 = Initialzustand der Maschine
                2 = Geraeteerfassung
                3 = festlegen der Netzadressen
                4 = Abfrage der Kanallisten
                5 = Master-Kommando bearbeitung
                6 = Kanaele lesen (Spot oder Parameter)
                7 = Kanaele schreiben (nur Parameter)"""
        result = self.YasdiMaster.GetMasterStateIndex()
        self.msg("Yasdi-Master Status: %s"%(result),0)
        return result

    def reset(self):
        """Setzt den Yasdi-Master in den Initialisierungszustand zurueck"""
        self.quit()
        self.__init__(self.driver,self.debug,self.max_devices)

    def load_devices(self):
        """Laed die gefunden Geraete per Unterklasse Device"""
        self.devicehandleslist = self.YasdiMaster.GetDeviceHandles()
        for i in self.devicehandleslist:
            if i != 0:
                self.DeviceList.append(Device(handle=i,master=self.YasdiMaster,debug=self.debug))

    def get_devices(self):
        """Gibt die geladenen Geraete wieder zurueck
                Ergebnis:
                Device-Klasse eines jeden Geraetes"""
        return self.DeviceList

class Device:
    """DeviceKlasse mit den moeglichen Eigenschaften und Methoden eines Geraetes (Wechselrichter und SunnyBC etc.)"""
    def __init__(self,handle,master,debug=0):
        """Konstruktor
                Parameter:
                handle = Geraetehandle
                master = Masterklasse
                debug = 0           Es werden bei 1 die DebugMsgs zurueckgegeben"""
        self.handle = handle
        self.master = master
        self.debug = debug
        self.channels = []

        result = self.update_all(nochannels=0)
        
        self.name = result[0]
        self.sn = result[1]
        self.type = result[2]

    def msg(self,msg,error=0):
        """msg Methode fuer Debug ausgaben etc.
                Parameter:
                msg =               Die Nachricht die ausgegeben / gespeichert werden soll
                error = 0           error = 0 Status error = 1 Fehlermeldung"""
        if error == 0: 
            if self.debug: print ":>        %s"%(msg)
        elif error == 1:
            if self.debug: print ":> Error: %s"%(msg)

    def update_name(self):
        """Aktualisiert den Geraetenamen und gibt ihn zurueck"""
        result = self.master.GetDeviceName(self.handle)
        self.msg("Geraetename %s"%(result),0)
        return result

    def update_sn(self):
        """Aktualisiert die GeraeteSN und gibt sie zurueck"""
        result = self.master.GetDeviceSN(self.handle)
        self.msg("GeraeteSN %s"%(result),0)
        return result

    def update_type(self):
        """Aktualisiert den Geraetetypen und gibt ihn zurueck"""
        result = self.master.GetDeviceType(self.handle)
        self.msg("Geraetetyp %s"%(result),0)
        return result

    def update_channels(self):
        """Aktualisiert die Kanaele des Geraetes und gibt die KanalHandles zurueck"""
        result = self.master.GetChannelHandles(handle=self.handle,parameter_channel=0)
        for i in result:
            if i != 0:
                self.channels.append(Channel(channel_handle=i,device_handle=self.handle,parameter_channel=0,master=self.master))
                self.msg("Geraetespotchannel      %s"%(i),0)

        result = self.master.GetChannelHandles(handle=self.handle,parameter_channel=1)
        for i in result:
            if i != 0:
                self.channels.append(Channel(channel_handle=i,device_handle=self.handle,parameter_channel=1,master=self.master))
                self.msg("Geraeteparameterchannel %s"%(i),0)
                
        return self.channels

    def update_all(self,noname=0,nosn=0,notype=0,nochannels=0):
        """Aktualisiert alles, das komplette Geraet
                Parameter:
                noname = 0          Namen des Geraetes nicht aktualisieren
                nosn = 0            SN des Geraetes nicht aktualisieren
                notype = 0          Typen des Geraetes nicht aktualisieren
                nochannels = 0      Kanaele des Geraetes nicht aktualisieren
                Ergebnis:
                Tupel (name,sn,type,channels)"""
        name = 0
        sn = 0
        typ = 0
        channels = 0
        
        if not noname: name = self.update_name()
        if not nosn: sn = self.update_sn()
        if not notype: typ = self.update_type()                 # type nicht erlaubt weil wegen Schluesselwort
        if not nochannels: channels = self.update_channels()

        return (name,sn,typ,channels)

    def get_name(self):
        """Gibt den GeraeteNamen zurueck"""
        return self.name

    def get_sn(self):
        """Gibt die GeraeteSN zurueck"""
        return self.sn

    def get_type(self):
        """Gibt den GeraeteTyp zurueck"""
        return self.type

    def get_channels(self):
        """Gibt die GeraeteKanaele zurueck"""
        return self.channels

    def get_formatted(self):
        """Formatierte Ausgabe des Geraetes, die Kanaele werden ink. Value einzeln aktualisiert"""
        print "Formatierter Bericht fuer Geraet %s:"%(self.get_name())
        for i in self.channels:
            name = i.update_name()
            value = i.update_value()
            unit = i.update_unit()
            if value == -3: self.msg("Channeltimeout fuer %s"%(i),1)
            else: print "%s  = %s%s"%(name,value[0],unit)

class Channel:
    """Konstruktor
            Parameter:
            channel_handle          HandleNummer dieses Kanals
            device_handle           GeraeteNummer dieses Kanals
            parameter_channel       0 = Spotwertkanal 1 = Parameterkanal
            max_channel_age = 60    max. Alter eines Spotwertkanals"""
    def __init__(self,channel_handle,device_handle,parameter_channel,master,max_channel_age=60):
        self.channel_handle = channel_handle
        self.device_handle = device_handle
        self.max_channel_age = max_channel_age
        self.master = master
        self.name = ""
        self.statustext = []            #Entweder Liste mit Statustexten oder wenn es keine fuer diesen Channel gibt  | -1 wenn Kanalhandle ungueltig
        self.unit = ""
        self.range = 0
        self.value = [0,"",0]           #(Wert,WertText,Timestamp)
        self.timestamp = 0

    def msg(self,msg,error=0):
        """msg Methode fuer Debug ausgaben etc.
                Parameter:
                msg =               Die Nachricht die ausgegeben / gespeichert werden soll
                error = 0           error = 0 Status error = 1 Fehlermeldung"""
        if error == 0: 
            if self.debug: print ":>        %s"%(msg)
        elif error == 1:
            if self.debug: print ":> Error: %s"%(msg)

    def update_statustext(self):
        """Ruft alle Statustexte zu einem Kanal ab und gibt sie als Liste zurueck"""
        result = self.master.GetChannelStatTextCnt(self.channel_handle)
        if not result:
            self.statustext = 0
        if result == -1:
            self.msg("Kanalhandle %s ungueltig fur Device %s"%(self.channel_handle,self.device_handle),1)
            self.statustext = -1
        else:
            for i in range(1,result):
                self.statustext.append(self.master.GetChannelStatText(self.channel_handle,i))
        return self.statustext

    def update_value(self):
        """Kanalwert aktualisieren, diese Methode braucht einige Sekunden. Gibt den Wert zurueck"""
        result = self.master.GetChannelValue(self.channel_handle,self.device_handle,0)
        if result == -3: return result
        else:
            channeltimestamp = self.update_timestamp()
            self.value[0] = result[0]
            self.value[1] = result[1]
            self.value[2] = channeltimestamp
            return result

    def update_timestamp(self):
        """Aktualisiert den Zeitstempel des Kanals und gibt ihn zurueck"""
        result = self.master.GetChannelValueTimeStamp(self.channel_handle)
        self.timestamp = result
        return result

    def update_range(self):
        """Aktualisiert den Kanalbereich und gibt ihn als Tupel zurueck"""
        result = self.master.GetChannelValRange(self.channel_handle)
        self.range = result
        return result

    def update_name(self):
        """Aktualisiert den Namen des Kanals und gibt ihn zurueck"""
        result = self.master.GetChannelName(self.channel_handle)
        self.name = result
        return result

    def update_unit(self):
        """Aktualisiert den Einheit (kWh) des Kanals und gibt ihn zurueck"""
        result = self.master.GetChannelUnit(self.channel_handle)
        self.unit = result
        return result

    def update_all(self,noname=0,nounit=0,nostatustext=0,novalue=1,norange=0):
        """Aktualisiert alles, den kompletten Kanal
                Parameter:
                noname = 0          Namen des Kanals nicht aktualisieren
                nounit = 0          Einheit des Kanals nicht aktualisieren
                nostatustext = 0    Statustext des Kanals nicht aktualisieren
                novalue = 1         Wert des Kanals nicht aktualisieren
                norange = 0         Wertebereich des Kanals nicht aktualisieren
                Ergebnis:
                Tupel (name,unit,statustext,value,range)"""
        statustext = []
        value = (0,"",0)
        valrange = ()
        unit = ""
        name = ""

        if not noname: name = self.update_name()
        if not nounit: unit = self.update_unit()
        if not nostatustext: statustext = self.update_statustext()
        if not novalue: value = self.update_value()
        if not norange: valrange = self.update_range()                 # range nicht erlaubt weil wegen Schluesselwort

        return (name,unit,statustext,value,valrange)

    def get_name(self):
        """Gibt den KanalNamen zurueck"""
        return self.name

    def get_unit(self):
        """Gibt die KanalEinheit zurueck"""
        return self.unit

    def get_statustext(self):
        """Gibt den KanalStatustext zurueck"""
        return self.statustext

    def get_value(self):
        """Gibt den KanalWert zurueck"""
        return self.value

    def get_range(self):
        """Gibt den KanalWerteBereicht zurueck"""
        return self.range    

if __name__ == "__main__":
    #main = pyYASDI()
    pass
