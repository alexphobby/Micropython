package com.example.hobbyapp

import android.content.ContentValues
import android.util.Log
import org.eclipse.paho.client.mqttv3.*
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence
import java.nio.charset.StandardCharsets
import java.time.Instant
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.util.*
import javax.net.ssl.SSLSocketFactory

data class MyHome(
    var rooms: List<Room> = listOf(Room())
)

data class Room(
    var roomName: String = "",
    var deviceName: String = "",
    var topic: Topic = Topic("to/$deviceName", "from/$deviceName"),
    var ambientLight: Double = 0.0,
    var humidity: Double = 0.0,
    var cameraMicaLed: Boolean = false,
    var dimPercent: Int = -1,
    var temperature: Double = 0.0,
    var lastMotion: Int = 0,
    var autoBrightness: Boolean = false,
    var isUpdated: Boolean = false,
    var lastUpdated: Date = Date.from(Instant.ofEpochSecond(0))
)

data class Topic(
    var topicForReceive: String = "",
    var topicForSending: String = ""
)

public class MqttUtilities(val cb: MqttCallback) {
    public lateinit var client: MqttClient
    public lateinit var options: MqttConnectOptions

    public var formatter: DateTimeFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")

    public fun Connect(): Boolean {
        if (this::client.isInitialized) {
            println("mqtt client is initialized, connected: ${client.isConnected}")

            if (client.isConnected) {
                println("mqtt Client is already connected")
                return true
            }
            else {
                println("mqtt client not connected, connecting..")
                client.connect()
                return true
            }
        }

        //cb = MyCallBack
        client = MqttClient(
            "ssl://fc284e6f2eba4ea29babdcdc98e95188.s1.eu.hivemq.cloud:8883",
            MqttClient.generateClientId(),
            MemoryPersistence()
        )

        options = MqttConnectOptions()
        options.userName = "apanoiu"
        options.password = "Mqtt741852".toCharArray()
        options.socketFactory = SSLSocketFactory.getDefault()


        try {
            client.connect(options)

        } catch (e: Exception) {
            Log.e(ContentValues.TAG, "mqtt error, ${e.toString()}")
            return false
        }

        //var cb = MyCallBack()
        println("mqtt init obj, set callback")
        client.setCallback(cb)
        val current = LocalDateTime.now().format(formatter)

        //room//.value?.forEach {
        //Log.d("DEBUG", "mqtt subscribing to: ${room.value?.topic?.topicForSending.toString()}")
//        client.subscribe("from_a36_cam_mica")
        //client.subscribe("from_a_baie")
        //}
        client.subscribe("from/#")
        client.subscribe("from/*")

        //client.subscribe("a36_cam_mica")
        //client.subscribe("a36_cam_medie")
        //client.subscribe("a36_cam_mare")
        //client.subscribe("fromCMica")

        var message = MqttMessage("Connected at $current".toByteArray(StandardCharsets.UTF_8))
        client.publish("android", message)
        return true
    }

    //@RequiresApi(Build.VERSION_CODES.O)
    private fun publishMessage(message: String, topic: String): String {
        var result: String = ""

        Log.d(
            "DEBUG",
            "mqtt publishMessage ${message}-${topic} ${this::client.isInitialized}"
        )

        val current = LocalDateTime.now().format(formatter)

        var mqttMessage = MqttMessage(message.toByteArray(StandardCharsets.UTF_8))

        if (!this::client.isInitialized) {
            println("mqtt publishmessage client not initialized, connecting")
            Connect()
        }

        if (!client.isConnected)
            client.connect(options)

        if (client.isConnected) {
            client.publish(topic, mqttMessage)
            result = "isConnected,published\n"
            return result
        }
        result = "issues"
        return result
    }

    fun requestStatuses(topic: String = "to/*") {
        //Connect()
        Log.d("DEBUG", "mqtt requestStatuses: discovery to : $topic")
        publishMessage("discovery", topic)

        //publishMessage("sendTemperature", "to/*")
        //publishMessage("sendTemperature", "to/a36_cam_mica")
        //publishMessage("sendTemperature", "to/a36_cam_medie")
        //publishMessage("sendTemperature", "to/a_baie")
    }

    fun setLightsPercent(deviceName: String, percent: Int) {
        Log.e("DEBUG", "mqtt setLightsPercent: $percent")
        publishMessage("lights:$percent", "to/${deviceName}")
        //requestStatuses("to/${deviceName}")

    }

    fun setAutoBrightness(deviceName: String, enabled: Boolean) {
        Log.d("DEBUG", "mqtt autobrightness:${enabled} to/${deviceName}")
        publishMessage("setAutoBrightness:${enabled}", "to/${deviceName}")

    }
}

public class TemperatureCallback(viewModel: MainViewModel) : MqttCallback {
    public var arrived = false

    //public var messageText = "x"
    public var myhome = MyHome()
    //lateinit var viewModel:MainViewModel

    public var rnd: Int = 0
    public var message = ""
    var vm = viewModel
init {
    //viewModel= MainViewModel()
    //var room = viewModel.roomsMutableList

}
    override fun connectionLost(cause: Throwable?) {
        Log.e(ContentValues.TAG, "mqtt Connection Lost")
    }

    override fun messageArrived(topic: String?, message: MqttMessage?) {
        this.message = message.toString()

        Log.e(ContentValues.TAG, "mqtt messageArrived: ${this.message} on topic: $topic")
        try {
            var key =""
            var value = ""
            val device = topic?.replace("from/", "") ?: return
            var countColon = this.message.count { it == ':' }
            //if (countColon > 1) {
                key = this.message.toString().split(":")[0]
                value = this.message.substring(startIndex = this.message.indexOfFirst { it == ':' }+1) //...split(":")[1:]

            println("mqtt key= $key, value=$value")
            //}
            //else {
             //   key = this.message.toString().split(":")[0]

            //}

            //Log.e(                ContentValues.TAG,                "mqtt messageArrived, topic: ${topic}, device: ${device}: key: ${key} -> $value"            )

            when (key) {
                "jsonDiscovery" -> {
                    vm.updateFromDiscovery(device, value)
                }
                "name" -> {
                    vm.updateRoomName(device, value)
                }
                "device" -> {
                    vm.updateRoomName(device, value)
                }


                "temperature" -> {
//                    Log.e(
//                        ContentValues.TAG,
//                        "mqtt messageArrived, update temperature: ${device} -> $value"
//                    )

                    vm.updateTemperatureToRoom(device, value.toDouble())
                    //viewModel._rooms//.update { it}
                    //arrived=true
                }
                "humidity" -> {
                    vm.updateHumidityToRoom(device, value.toDouble())
                }
                "ambient" -> {
                    vm.updateAmbientLightToRoom(device, value.toDouble())
                }
                "dim" -> {
                    vm.updateDimPercentToRoom(device, value.toInt())
                }
                "lastmotion" -> {
                    vm.updateLastMotionToRoom(device, value.toInt())
                }

            }
        } catch (e: Exception) {
            Log.e(ContentValues.TAG, "mqtt error messageArrived, $e")
        }

    }

    override fun deliveryComplete(token: IMqttDeliveryToken?) {
        //Log.e(ContentValues.TAG, "mqtt delivered")
    }


}