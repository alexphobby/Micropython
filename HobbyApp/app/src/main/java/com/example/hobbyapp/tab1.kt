package com.example.hobbyapp

//import androidx.compose.material.ExperimentalMaterialApi

//import androidx.compose.material3.pullrefresh.pullRefresh
//import androidx.compose.material3.pullrefresh.rememberPullRefreshState
//import androidx.lifecycle.viewmodel.compose.viewModel
import android.util.Log
import android.widget.Toast
import androidx.compose.animation.Crossfade
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.ExperimentalMaterialApi
import androidx.compose.material.pullrefresh.PullRefreshIndicator
import androidx.compose.material.pullrefresh.pullRefresh
import androidx.compose.material.pullrefresh.rememberPullRefreshState
import androidx.compose.material3.Card
import androidx.compose.material3.Checkbox
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.io.File
import java.util.TimeZone
import kotlin.math.roundToInt

fun getCards() {
    return
}


//@OptIn(ExperimentalMaterialApi::class)
@ExperimentalMaterialApi
@Composable
fun Tab1() {

    val vm: MainViewModel = viewModel()
    //val refreshing by viewModel.
    val refreshScope = rememberCoroutineScope()

    var refreshing by rememberSaveable { mutableStateOf(false) }
    var itemCount by remember { mutableStateOf(15) }

    val pullRefreshState = rememberPullRefreshState(refreshing, { vm.refresh() })
    val composableScope = rememberCoroutineScope()
//viewModel.refresh()
    //vm.onUpdate.value
    //vm.roomsMutable
    val logFile = File("/storage/emulated/0/Download/log.txt")

    var scrollMemory by rememberSaveable { mutableStateOf(0f) }
    //val testMutable by vm.roomMutable.observeAsState(0)

    //val refreshScope = rememberCoroutineScope()
    //var refreshing by rememberSaveable { mutableStateOf(false) }

    println("mqtt render tab1")
    //vm.mqtt.requestStatuses()
    fun refresh() = refreshScope.launch {
        refreshing = true
        delay(1500)
        itemCount += 5
        refreshing = false
    }
    val state = rememberPullRefreshState(refreshing, ::refresh)


    Box(Modifier.pullRefresh(state)) {
        LazyColumn(Modifier.fillMaxWidth(), contentPadding = PaddingValues(16.dp)) {
            itemsIndexed(vm.roomsMutable) { index, item ->

                logFile.appendText("mqtt item, index=$index: item= ${item.roomName}")
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .wrapContentHeight()
                        .padding(vertical = 25.dp),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {

                    CardBirou2(room = item,mainViewModel = vm)
                    //Text(item.temperature.toString(), color = Color.White)
                    //CardBirou(item.value.
                    //   .roomName,item.ambientLight,item.dimPercent,item.temperature,item.humidity,mainViewModel)
                }
            }


            /*if (!refreshing) {

                Log.e(ContentValues.TAG,"mqtt pullrefreshstate")
                try {
                    vm.mqtt.requestStatuses()
                }
                catch (ex:Exception) {
                    println("mqtt error $ex")
                    logFile.appendText(
                        "mqtt pullrefresh error $ex")
                }


            }*/
        }

        PullRefreshIndicator(refreshing, state, Modifier.align(Alignment.TopCenter))
    }
    //val pullRefreshState = rememberPullRefreshState(refreshing,{
        //vm.roomsMutable.clear()
        //vm.mqtt.requestStatuses()
//        val myWorkRequest = OneTimeWorkRequestBuilder<MqttWorker>()
//            .setInputData(inputData = workDataOf("ACTION" to "REFRESH"))
//            .build()



    //    composableScope.launch
    /*{

            Log.e(ContentValues.TAG,"mqtt pullrefreshstate")
            logFile.appendText("mqtt pullrefresh before emptylist: ${vm.roomsMutable.toList().isEmpty()}, refreshing: ${refreshing}\n")
            //vm.refresh()

            try {
                vm.mqtt.Connect()
            }
            catch (ex:Exception) {
                println("mqtt error $ex")
                logFile.appendText(
                    "mqtt pullrefresh error $ex")
            }

            try {
                vm.mqtt.requestStatuses()
            }
            catch (ex:Exception) {
                println("mqtt error $ex")
                logFile.appendText(
                    "mqtt pullrefresh error $ex")
            }
            logFile.appendText(
                "mqtt pullrefresh after emptylist: ${
                    vm.roomsMutable.toList().isEmpty()
                }, refreshing: ${refreshing} \n"
            )
            logFile.appendText("recompose\n")
            //vm.refresh()
        }*/
  //  })




    //val roomsMutable by rememberSaveable { mutableStateListOf(Room)}

    //val rl =
    //var roomListMutable = remember { mutableStateListOf<Room>() }
    //roomListMutable = rl
    //val home by mainViewModel.mqttData.collectAsState()

//    val tmp by mainViewModel.temperatureData.collectAsState()
    //var roomList = mainViewModel.roomList

    //Column(modifier = Modifier.verticalScroll(state = ScrollState(scrollMemory.toInt()))) {
    //   CardBirou("a36_cam_medie",mainViewModel)
    //  CardBirou("a36_cam_mica",mainViewModel)
    //CardBirou("a36_cam_mica",mainViewModel)
    //Text(vm.roomsMutable?.count().toString())
//
//    LaunchedEffect(Unit ) {
//        Log.e(ContentValues.TAG,"mqtt tab1 LaunchedEffect")
//        //vm.mqtt.requestStatuses()
//        composableScope.launch {
//            vm.refresh()
//        }
//        logFile.appendText("launchedeffect vm refresh\n")
//
//    }
    //Log.e(ContentValues.TAG,"mqtt emptylist: ${vm.roomsMutable.toList().isEmpty()}")
    //logFile.appendText("mqtt emptylist: ${vm.roomsMutable.toList().isEmpty()},  \n")
    /*if (false) {

//    if (vm.roomsMutable.toList().isEmpty() && refreshing) {
//        Box(modifier = Modifier
//            //.fillMaxSize()
//            .pullRefresh(pullRefreshState)
//        ) {
          Text("No device discovered yet, pull down to refresh", color = Color.White)
//            //vm.mqtt.requestStatuses()
//
//            vm.refresh()
//            PullRefreshIndicator(refreshing, pullRefreshState, modifier = Modifier.align(Alignment.TopCenter))
//        }
//
//
    }
    else {



        Box(
            modifier = Modifier
                .pullRefresh(pullRefreshState)
        ) {

//            if(vm.roomsMutableList.isEmpty()) {
//                Text("No device discovered yet, pull down to refresh", color = Color.White)
//            }

//            //PullRefreshIndicator(refreshing, pullRefreshState, modifier = Modifier.align(Alignment.TopCenter))
            // }
//        Box(//modifier = Modifier
//            //.pullRefresh(pullRefreshState)
//        ) {

            LazyColumn(
                modifier = Modifier
                    .fillMaxWidth(),
                contentPadding = PaddingValues(16.dp)
            ) {
                itemsIndexed(vm.roomsMutable) { index, item ->

                    logFile.appendText("mqtt item, index=$index: item= ${item.roomName}")
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .wrapContentHeight()
                            .padding(vertical = 25.dp),
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
//                Text(
//                    "\uD83C\uDF3F  Plants in Cosmetics",
//                    style = MaterialTheme.typography.bodyMedium, color = Color.White

                        //)
                        //Log.e("Compose","mqtt ${item .temperature}")
                        //Text(item.temperature.toString(), color = Color.Black)
//                        CardBirou(
//                            cardRoomName = item.roomName,
//                            ambientLight = item.ambientLight,
//                            dimPercent = item.dimPercent,
//                            temperature = item.temperature,
//                            humidity = item.humidity,
//                            mainViewModel = vm
//                        )
                        CardBirou2(room = item,mainViewModel = vm)
                        //Text(item.temperature.toString(), color = Color.White)
                        //CardBirou(item.value.
                        //   .roomName,item.ambientLight,item.dimPercent,item.temperature,item.humidity,mainViewModel)
                    }
                }

            }
            PullRefreshIndicator(
                refreshing,
                pullRefreshState,
                modifier = Modifier.align(Alignment.TopCenter)
            )

        }
    }*/
}


// mqtt.requestTemperature()

@Preview
@Composable
fun preview() {
    var vm = MainViewModel()
    var memoryIsVisible = true
    //androidx.compose.material.Text(text = "caca", color = Color.White)
    CardBirou2(room = Room("Test"), mainViewModel = vm,true)
}
@Composable
fun CardBirou2(
    room: Room,
    mainViewModel: MainViewModel,
    test:Boolean = false
) {
    val composableScope = rememberCoroutineScope()
    //mainViewModel.onUpdate.value
    /*val roomName by mainViewModel.roomName.collectAsState()

    val ambientLight by mainViewModel.ambientLight.collectAsState()

    val dimPercent by mainViewModel.dimPercent.collectAsState()
    val dimPercentSlider by mainViewModel.dimPercentSlider.collectAsState()

    val temperature by mainViewModel.temperature.collectAsState()
    val humidity by mainViewModel.humidity.collectAsState()
*/
    val cardHeight = 0
    var cardSize = 300.dp

    var checkedState by rememberSaveable { mutableStateOf(false) }
    var memoryIsVisible  by rememberSaveable { mutableStateOf(false) }
    var minutesAgo:Int = 0

    if(test) {
        memoryIsVisible = true
    }
    //var dimPercentSliderChanged by rememberSaveable { mutableStateOf(false) }

    //var dimSliderValue = 0

    val cardModifier = Modifier
        .padding(start = 20.dp, end = 20.dp, bottom = 20.dp)
        .fillMaxWidth()
        .height(280.dp)

    val boxModifier = Modifier
        .fillMaxSize()
        .background(Color.DarkGray)

    //Log.e(ContentValues.TAG, "mqtt composinng: RN: $cardRoomName")
    Card(
        modifier = cardModifier
            .onSizeChanged {

                cardSize = cardHeight.dp + 100.dp

            }
    )

    {
        var sliderPosition by rememberSaveable { mutableStateOf(0f) } //dimPercent.toFloat()/100) }
        var sliderPositionMemory by rememberSaveable { mutableStateOf(0f) }
        var sliderChanging by rememberSaveable { mutableStateOf(false) } //dimPercent.toFloat()/100) }

        //sliderPosition = dimPercent.toFloat()/100


//        Log.e(
//            "LOG",
//            "mqtt recompose tab "
//        )

//


//        Image(painter = painterResource(id = R.drawable.munte_cu_copiii),
//            contentDescription = "test munte",
//            contentScale = ContentScale.Crop,
//            modifier = Modifier.clip(RoundedCornerShape(20.dp))
//        )
        Box(
            modifier = boxModifier
        ) {
            Column() {
                Row() {
                    Text(
                        text = room.roomName,
                        modifier = Modifier.padding(all = 10.dp),
                        color = Color.White,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold
                    )
                }

                var context = LocalContext.current


                Row() {
                    Text(
                        text = "Switch lights",
                        modifier = Modifier.padding(start=14.dp,top=14.dp),
                        color = Color.White
                    )
                    Switch(checked = room.dimPercent > 0,
                        modifier = Modifier,
                        onCheckedChange = {
                            Log.e("LOG", "mqtt ${it.toString()}")

                            if (!it) {
                                composableScope.launch {

                                    mainViewModel.updateDimPercentToRoomName(room.roomName, 0)
                                    mainViewModel.mqtt.setLightsPercent(room.deviceName, 0)
                                    memoryIsVisible = sliderPositionMemory > 0
                                    Log.e("LOG", "mqtt Switch off, memory is visible: $memoryIsVisible")
                                }
//                                sliderPosition = 0f
//                                Log.e("LOG", "mqtt slider to 0 ${sliderPosition.toString()}")
                                //mainViewModel.mqtt.setLightsPercent((sliderPosition*100).toInt())
                            } else {

                                Log.e("LOG", "mqtt Switch on")
                                memoryIsVisible = false
                                if (sliderPositionMemory > 0) {
                                    sliderPosition = sliderPositionMemory
                                    Log.e("LOG", "mqtt Switch memory")
                                } else {
                                    sliderPosition = 0.5f
                                }
                                composableScope.launch {
                                    mainViewModel.updateDimPercentToRoomName(
                                        room.roomName,
                                        (sliderPosition * 100).roundToInt()
                                    )
                                    mainViewModel.mqtt.setLightsPercent(
                                        room.deviceName,
                                        (sliderPosition * 100).roundToInt()
                                    )
                                    //Log.e("LOG", "mqtt Switch Move slider to: ${dimPercent.toString()}")
                                }
                                //Log.e("LOG", "mqtt slider to ${sliderPosition.toString()}")
                            }

                            //mainViewModel.mqtt.setLightsPercent(dimPercent)
                            checkedState = it
                            //memoryIsVisible = sliderPositionMemory > 0 && !checkedState


                        }
                    )
                    Text(text = "Auto:", modifier = Modifier
                        .padding(start=14.dp,top = 14.dp)
                        , color = Color.White)

                    //val checkedState = remember { mutableStateOf(true) }
                    Checkbox(checked = room.autoBrightness,modifier = Modifier //.padding(top=0.dp)
                        , onCheckedChange = {//it = valoarea ceruta
                            println("mqtt $it")
                            if ((sliderPosition == 0f && it) ) {
                                println("mqtt slider = $sliderPosition")
                                Toast.makeText(context.applicationContext,"Cannot set auto = 0",Toast.LENGTH_LONG).show()
                               // return@Checkbox
                            }

                            room.autoBrightness = it
                            mainViewModel.mqtt.setAutoBrightness(
                                //mainViewModel.getDeviceNameFromRoomName(
                                room.deviceName,enabled = it )                       })

                    if (memoryIsVisible) {
                        Text(
                            text = "M: ${(sliderPositionMemory * 100).toInt()}",
                            textAlign = TextAlign.End,
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 14.dp, end = 10.dp),
                            color = Color.White
                        )
                    }


                } //Switch lights
                Row() {


                    //Text(sliderPosition.toString(),modifier=Modifier.padding(start = (sliderPosition *100).dp))
                    if ((sliderPosition * 100).roundToInt() != room.dimPercent && room.isUpdated) {
                        //Log.e("LOG", "mqtt slider different $sliderPosition, rounded: ${(sliderPosition*100).roundToInt()} , ${room.dimPercent}}")
                        sliderPosition = room.dimPercent.toFloat()/100

                    }
                    Slider(
                        value = sliderPosition, //room.dimPercent.toFloat() / 100, //sliderPosition,
                        onValueChange = {
                            //Log.e("LOG", "mqtt ValueChanged ${(sliderPosition*100).toString()}")
                            //sliderPosition = it
//                            mainViewModel.updateDimPercentToRoomName(
//                                room.roomName,
//                                (it * 100).roundToInt()
//                            )
                            sliderChanging =true
                            room.isUpdated = false

                            sliderPosition = it
                            if (it > 0) {
                                sliderPositionMemory = it
                                //println("mqtt sliderpositionmemory: $sliderPositionMemory, memoryIsVisible: $memoryIsVisible")


                            }
//                            Log.e(
//                                "LOG",
//                                "mqtt ValueChanged ${((it * 100).roundToInt()).toString()}"
//                            )
////                            mainViewModel.mqtt.setLightsPercent(
//                                //mainViewModel.getDeviceNameFromRoomName(
//                                room.deviceName,(it * 100).roundToInt()
//                            )
//                            mainViewModel.mqtt.requestStatuses(room.topic.topicForReceive)

                        },
                        onValueChangeFinished = {
                            //dimPercentSliderChanged =true
                            sliderPosition = ((sliderPosition*100).roundToInt().toFloat()/100)
                            sliderChanging = false
//                            Log.e(
//                                "LOG",
//                                "mqtt ValueChangedfinished ${((sliderPosition * 100).roundToInt()).toString()}"
//                            )
                            composableScope.launch {
                                mainViewModel.mqtt.setLightsPercent(
                                    //mainViewModel.getDeviceNameFromRoomName(
                                    room.deviceName, (sliderPosition * 100).roundToInt()
                                )
                                //mainViewModel.mqtt.requestStatuses(room.topic.topicForReceive)


                            }
                        },  //,steps=5
                    steps = 100
                    )

                } //Slider


                Row() {
                    if (true) {
                        Column() {

                            //Text("Changed $tmp", color = Color.White)

                            Text(
                                "Temp: ${room.temperature.toString()}",
                                modifier = Modifier.padding(start = 20.dp),
                                color = Color.White
                            )

                            Text(
                                "Humidity: ${room.humidity.toString()} %",
                                modifier = Modifier.padding(start = 20.dp),
                                color = Color.White
                            )
                            Text(
                                "Ambient light: ${room.ambientLight.toString()} lux",
                                modifier = Modifier.padding(start = 20.dp),
                                color = Color.White
                            )


                            Row {

                                Text(
                                    "Light: ",
                                    modifier = Modifier
                                        .padding(start = 20.dp),
                                    color = Color.White
                                )
                                //AnimatedContent(targetState = dimPercent) { targetState ->
                                Crossfade(targetState = room.dimPercent) { targetState ->
                                    //    Text(" ${dimPercent.toString()} %",
                                    Text(
                                        " ${targetState.toString()} %",
                                        modifier = Modifier,
                                        color = Color.White
                                    )

                                    //sliderPosition = (dimPercent.toFloat() / 100)
//                                    if (mainViewModel.initState && dimPercent > -1) {
//                                        Log.e(
//                                            "LOG",
//                                            "mqtt InitState ${(dimPercent).toString()}"
//                                        )
//                                        sliderPosition = (dimPercent.toFloat() / 100)
//                                        mainViewModel.initState = false
//                                    }


                                }



                            }

                            minutesAgo = (( (TimeZone.getDefault().dstSavings + TimeZone.getDefault().rawOffset + System.currentTimeMillis())/1000 - room.lastMotion)/60).toInt()
//                            println("mqtt  now: ${System.currentTimeMillis()/1000}  dst: ${TimeZone.getDefault().dstSavings} offset: ${TimeZone.getDefault().rawOffset}")
//                            println("mqtt current ${System.currentTimeMillis()/1000 + TimeZone.getDefault().dstSavings + TimeZone.getDefault().rawOffset}")
//                            println("mqtt lastmotion ${room.lastMotion}")
//                            println("mqtt ${(( (TimeZone.getDefault().dstSavings + TimeZone.getDefault().rawOffset + System.currentTimeMillis())/1000 - room.lastMotion)/60).toInt()}")

                            //val logFile = File("/storage/emulated/0/Download/log.txt")

                            //logFile.appendText("mqtt item, minutesago= $minutesAgo, time=${System.currentTimeMillis()/1000/60}, lastmotion: ${(room.lastMotion/60)}")

                            if (minutesAgo < 120) {
                                Row() {

                                    //java.time.format.DateTimeFormatter.ISO_INSTANT.format(java.time.Instant.ofEpochSecond(room.lastMotion.toLong()))
                                    Text(
                                        text = "Motion: ${minutesAgo} minutes ago",
                                        modifier = Modifier.padding(start = 20.dp),
                                        color = Color.White
                                    )
                                }
                            }
                            Box(modifier = Modifier.height(30.dp))
                        }

                    } else {
                        //Text("no change ${Random.nextInt()}", color = Color.White)
                    }


                } //Details

            }

            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        brush = Brush.verticalGradient(
                            colorStops = arrayOf(0.8f to Color.Transparent, 1f to Color.Black),
                            startY = 0.3f
                        )
                    )
            )

            Box(
                modifier = Modifier
                    .offset(0.dp, cardSize - 20.dp)

            ) {
//                Text(text = "111111111", color = Color.LightGray, fontSize = 20.sp)


            }
        }
    }


}
