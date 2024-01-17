package com.example.hobbyapp

import android.content.Context
import androidx.work.Worker
import androidx.work.WorkerParameters

//import androidx.work.Worker
//import androidx.work.WorkerParameters

class MqttWorker(context: Context, workerParams: WorkerParameters) : Worker(context, workerParams)
{
    override fun doWork(): Result {
        val appContext = applicationContext
        var vm = MainViewModel()

        val message = inputData.getString("ACTION")
        println("mqtt worker init, data = $message")

        if(message == "INIT") {
            vm.init()
            vm.refresh()
            //Thread.sleep(5000)
        }
        if(message == "REFRESH") {
            //Thread.sleep(5000)
            vm.refresh()
//            Thread.sleep(5000)
        }
        println("mqtt worker timer done")
        //vm.refresh()
        println("mqtt exit worker")
        return Result.success()


    }
}