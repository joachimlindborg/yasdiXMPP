about = """
Titel: yasdiwrapper
Autor: Sebastian Schulte
Version: 1.0.0
Datum: 18.3.07 / 18.3.07 / 18.3.07
Datei: yasdiwrapper.py

+ SMA YASDI Library Wrapper fuer Python Scripting Language v1"""
import ctypes,array         #ctypes laed die Libs in Python, array (BuildIn) fuer C Arrays

class YasdiMaster:
    def __init__(self,
                 ini_file="./yasdi.ini",
                 yasdiMaster_lib="./libyasdimaster.so",
                 iDeviceHandleCount=50,
                 iChannelHandleCount=142,
                 DeviceNameBuffer=30,
                 DeviceTypeBuffer=30,
                 ValText=15,
                 ChannelName=30,
                 cChanUnit=10,
                 status_text_buffer=30):
        """Konstruktor
                Parameter:
                ini_file = "yasdi.ini"                |erwartet Pfad zur ini Datei (mit Schnittstelleninformationen etc.)
                yasdiMaster_lib = "libyasdimaster.so" |erwartet Pfad zur yasdimaster Lib
                iDeviceHandleCount = 50               |Anzahl der max. zu erfassenden Geraete
                iChannelHandleCount = 142             |Anzahl der max. zu erfassenden Kanaele
                DeviceNameBuffer = 30                 |Anzahl der max. Namenslaenge eines Geraetes
                DeviceTypeBuffer = 30                 |Anzahl der max. Namenslaenge eines Geraetetypes
                ValText = 15                          |Anzahl der max. Namenslaenge eines Textes der zu einem Kanal gehoert
                ChannelName = 30                      |Anzahl der max. Namenslaenge eines Kanalnamens
                cChanUnit = 10                        |Anzahl der max. Namenslaenge einer Kanaleinheit (z.B. kWp)
                status_text_buffer = 30               |Anzahl der max. Nameslaenge eines Statustextes zu einem Kanal"""
        self.ini_file = ini_file
        self.yasdiMaster_lib = yasdiMaster_lib
        self.DriverCount = ctypes.c_ulong()
        self.pDriverCount = ctypes.pointer(self.DriverCount)
        self.iDeviceHandleCount = iDeviceHandleCount
        self.DeviceHandles = array.array("L",[0]*self.iDeviceHandleCount)
        self.iChannelHandleCount = iChannelHandleCount
        self.ChannelHandles = array.array("L",[0]*self.iChannelHandleCount)
        self.DeviceNameBuffer = " "*DeviceNameBuffer
        self.DeviceTypeBuffer = " "*DeviceTypeBuffer
        self.SNBuffer = ctypes.c_ulong()
        self.pSNBuffer = ctypes.pointer(self.SNBuffer)
        self.dDevHandle = ctypes.c_ulong()
        self.pdDevHandle = ctypes.pointer(self.dDevHandle)
        self.ChannelName = " "*ChannelName
        self.dblValue = ctypes.c_double(0)
        self.pdblValue = ctypes.pointer(self.dblValue)
        self.ValText = " "*ValText
        self.cChanUnit = " "*cChanUnit
        self.status_text_buffer = " "*status_text_buffer
        self.ChanType = ctypes.c_ushort()
        self.pChanType = ctypes.pointer(self.ChanType)
        self.ChanIndex = ctypes.c_int()
        self.pChanIndex = ctypes.pointer(self.ChanIndex)
        self.range_min = ctypes.c_double()
        self.prange_min = ctypes.pointer(self.range_min)
        self.range_max = ctypes.c_double()
        self.prange_max = ctypes.pointer(self.range_max)
        
        self.yasdiMaster = ctypes.cdll.LoadLibrary(self.yasdiMaster_lib)

    def yasdiMasterInitialize(self):
        """Initialisiert die yasdiMaster Lib, diese Mathode muss zuerst aufgerufen werden."""
        self.yasdiMaster.yasdiMasterInitialize(self.ini_file,self.pDriverCount)

    def yasdiMasterShutdown(self):
        """Beendet die yasdiMaster Lib, diese Methode gibt alle Resourcen wieder frei."""
        self.yasdiMaster.yasdiMasterShutdown()

    def yasdiReset(self):
        """Setzt die yasdiMaster Lib wiedr in den Ursprungszustend... wie nach yasdiMasterInitialize"""
        self.yasdiMaster.yasdiReset()

    def GetDeviceHandles(self):
        """Gibt alle GeraeteHandles zurueck (typ: Liste)"""
        self.yasdiMaster.GetDeviceHandles(self.DeviceHandles.buffer_info()[0],
                                           self.iDeviceHandleCount)
        return self.DeviceHandles.tolist()

    def GetDeviceName(self,handle):
        """Gibt zu dem GeraeteHandle den Geraetenamen als String zurueck
                Parameter:
                handle = Geraetehandle"""
        self.yasdiMaster.GetDeviceName(handle,self.DeviceNameBuffer,len(self.DeviceNameBuffer))

        return self.DeviceNameBuffer.replace("\x00","").rstrip()

    def GetDeviceSN(self,handle):
        """Gibt zu dem GeraeteHandle die Seriennummer zurueck, fuehrende Nullen werden entfernt da das Ergebnis numerisch ist
                Parameter:
                handle = Geraetehandle"""
        self.yasdiMaster.GetDeviceSN(handle,self.pSNBuffer)
        return int(self.SNBuffer.value)

    def GetDeviceType(self,handle):
        """Gibt zu dem GeraeteHandle den Typ (z.B. SunBC-38) zrueck
                Parameter:
                handle = Geraetehandle"""
        result = self.yasdiMaster.GetDeviceType(handle,self.DeviceTypeBuffer,len(self.DeviceTypeBuffer))
        if result == -1:
            return result
        else:
            return self.DeviceTypeBuffer.replace("\x00","").rstrip()

    def GetChannelHandles(self,handle,parameter_channel=0):
        """Gibt die ChannelHandles zurueck.
                handle = erwartet das entsprechende Handle des Geraetes
                parameter_channel = 0 -> Spotwerte| 1 -> Parameterwerte"""
        if parameter_channel == 1:
            wChanType = ctypes.c_ushort(0x040f)
        elif parameter_channel == 0:
            wChanType = ctypes.c_ushort(0x090f)
        else:
            return -1

        bChanIndex = ctypes.c_byte(0)
        self.yasdiMaster.GetChannelHandles(handle,
                                            self.ChannelHandles.buffer_info()[0],
                                            self.iChannelHandleCount,
                                            wChanType,
                                            bChanIndex)
        
        return self.ChannelHandles.tolist()

    def FindChannelName(self,name):
        """Gibt zu einen Kanalnamen den Wert und das Handle zurueck
                Parameter:
                name = Kanalnamen"""
        channel_value = self.yasdiMaster.FindChannelName(self.pdDevHandle,name)
        if channel_value == 0:
            return channel_value
        else:
            return (channel_value,self.dDevHandle.value)

    def GetChannelName(self,handle):
        """Gibt den ChannelNamen zurueck. -1 bei Misserfolg
                Parameter:
                handle = erwartet den entsprechenden Handle des Channels"""
        result = self.yasdiMaster.GetChannelName(handle,self.ChannelName,len(self.ChannelName))
        if result == -1:
            return result
        else:
            return self.ChannelName.replace("\x00","").rstrip().lstrip()

    def GetChannelValue(self,channel_handle,device_handle,max_val_age=0):
        """Gibt den Wert einen Channels zu einem Device zurueck.
                Parameter:
                channel_handle = erwartet einen KanalHandle (Parameter oder Spot)
                device_handle = erwartet eine DeviceHandle
                max_val_age = maximales Alter in Sekunden, die YASDI Lib wartet darauf (!!)| Std. sind 10Sekunden

                Rueckgabe:
                Tupel: (Wert,wenn vorhanden Text)
                -1: Kanalhandle falsch
                -2: YASDI Status ShutDown
                -3: Timeout
                -4: Unbekannter Fehler; Kanalwert ungueltig"""
        result = self.yasdiMaster.GetChannelValue(channel_handle,
                                                   device_handle,
                                                   self.pdblValue,
                                                   self.ValText,
                                                   len(self.ValText),
                                                   max_val_age)
        if result == 0:
            return (self.dblValue.value,self.ValText.replace("\x00","").rstrip().lstrip())
        else:
            return result
        

    def GetChannelValueTimeStamp(self,handle):
        """Sekunden der Epoche, wenn Rueckgabe Null dann ist das Handle ungueltig
                Parameter:
                handle = Kanalhandle"""
        timestamp = self.yasdiMaster.GetChannelValueTimeStamp(handle)
        return timestamp

    def GetChannelUnit(self,handle):
        """Gibt die Einheit eines Kanals zurueck. z.B. [Pac]=kW
                Parameter:
                handle = Kanalhandle"""
        self.yasdiMaster.GetChannelUnit(handle,self.cChanUnit,len(self.cChanUnit))
        return self.cChanUnit.replace("\x00","").rstrip().lstrip()

    def GetMasterStateIndex(self):
        """Gibt den Status des yasdiMasters zurueck:
                1 = Initialzustand der Maschine
                2 = Geraeteerfassung
                3 = festlegen der Netzadressen
                4 = Abfrage der Kanallisten
                5 = Master-Kommando bearbeitung
                6 = Kanaele lesen (Spot oder Parameter)
                7 = Kanaele schreiben (nur Parameter)"""
        result = self.yasdiMaster.GetMasterStateIndex()
        return result

    def SetChannelValue(self,channel_handle,device_handle,value):
        result = self.yasdiMaster.SetChannelValue(channel_handle,device_handle,value)
        return result
    
    def GetChannelStatTextCnt(self,handle):
        """Gibt die Anzahl der Statustechte des Kanals zurueck
                Parameter:
                handle = Kanalhandle"""
        result = self.yasdiMaster.GetChannelStatTextCnt(handle)
        return result

    def GetChannelStatText(self,handle,index,):
        """Gibt den Statustext des Kanals zurueck
                Parameter:
                handle = Kanalhandle
                index = Index des Statustextes, beginnend bei 0"""
        result = self.yasdiMaster.GetChannelStatText(handle,index,self.status_text_buffer,len(self.status_text_buffer))
        if not result:
            return self.status_text_buffer.replace("\x00","").rstrip().lstrip()
        else:
            return result

    def GetChannelMask(self,handle):
        """Gibt die ChannelMast zurueck, d.h. ob die Kanaele Spot oder Parameterkanaele sind
                Parameter: Kanalhandle"""
        result = self.yasdiMaster.GetChannelMask(handle,self.pChanType,self.pChanIndex)
        return (self.ChanType.value,self.ChanIndex.value)
        

    def DoMasterCmdEx(self,device_handle_count,cmd="detection",param1=None,param2=None):
        """Sendet Kommandos an den YASDI-Master. In YASDI 1.3 gibt es nur das Cmd "detection"
                Parameter:
                device_handle_count = Anzahl der zu suchenden Geraete
                cmd = "detection" , das einzige Cmd ist voreingestellt und sucht nach Geraeten
                param1 = None k.a.
                param2 = None k.a.
                Ergebnis:
                0 = OK
                -1 = es wurden nicht alle Geraete erreicht"""
        result = self.yasdiMaster.yasdiDoMasterCmdEx(cmd,device_handle_count,param1,param2)
        return result

    def GetChannelValRange(self,handle):
        """Gibt den Bereich des Kanals zurueck. z.B. Kanal 82 (DA_Messintervall von 0 - 240)
                Parameter:
                handle = Kanalhandle
                Ergebnis:
                Python Tupel(min,max) bei OK
                -1: Kanalhandle ist ungueltig
                -2: Zeiger fuer Ergebnis ungueltig (sollte durch den yasdiwrapper nicht vorkommen)
                -3: wenn es keinen extra Wertebereich gibt
                """
        result = self.yasdiMaster.GetChannelValRange(handle,self.prange_min,self.prange_max)
        if not result:
            return (self.range_min.value,self.range_max.value)
        else:
            return result

class Yasdi:
    """YASDI Wrapper fuer Python"""
    def __init__(self,yasdi_lib="./libyasdi.so",maxDriverIDs=10,DriverNameBuffer=30):
        """Konstruktor
                Parameter:
                yasdi_lib = "libyasdi.so"       |erwartet Pfad zur yasdi Lib
                maxDriverIDs = 10               |Anzahl der max. moegleichen Schnittstellen
                DriverNameBuffer = 30           |Anzahl der max.Namenslaenge des Schnittstellennamens"""
        self.maxDriverIDs = maxDriverIDs
        self.DriverIDArray = array.array("L",[0]*self.maxDriverIDs)
        self.DriverNameBuffer = " "*DriverNameBuffer

        self.yasdi = ctypes.cdll.LoadLibrary(yasdi_lib)

    def yasdiGetDriver(self):
        """Gibt die Anzahl zur verfuegung stehender Schnittstellen zurueck"""
        result = self.yasdi.yasdiGetDriver(self.DriverIDArray.buffer_info()[0],self.maxDriverIDs)
        return result

    def yasdiGetDriverName(self,driverID):
        """Gibt den Namen eine Schnittstelle zurueck, zum Beispiel: COM1 oder /drv/ttyS0 etc.
                Parameter:
                driverID = erwartet Schnittstellnummer (z.B. 0)"""
        self.yasdi.yasdiGetDriverName(driverID,self.DriverNameBuffer,len(self.DriverNameBuffer))
        return self.DriverNameBuffer.replace("\x00","").rstrip().lstrip()

    def yasdiSetDriverOnline(self,driverID):
        """Setzt eine Schnittstelle(driver) online, Achtung: unter Linux muss die Schnittstelle freigegeben werden!
                Parameter:
                driverID = Nummer der Schnittstelle (Com1 = 0 etc.)
                Rueckgabe:
                0: bei Erfolg
                1: bei Fehler"""
        result = self.yasdi.yasdiSetDriverOnline(driverID)
        return result

    def yasdiSetDriverOffline(self,driverID):
        """Gibt die Schnittstelle wieder Frei
                Parameter:
                driverID = erwartet Schnittstellnummer (z.B. 0)"""
        self.yasdi.yasdiSetDriverOffline(driverID)

if __name__ == "__main__":
    print about
    Master = YasdiMaster()
    Slave = Yasdi()

    Master.yasdiMasterInitialize()

    print "hole Driver(>0)       :",Slave.yasdiGetDriver()
    print "setze Driver Online(1):",Slave.yasdiSetDriverOnline(6)
    print "Geraete erfassen(0)   :",Master.DoMasterCmdEx(1)   #ein Geraet erfassen
    
    print Master.GetChannelValue(2,1)

    Master.yasdiMasterShutdown()
    raw_input("Eingabe")

