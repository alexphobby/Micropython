package com.example.hobbyapp

//import androidx.compose.foundation.pager.rememberPagerState

// for a 'val' variable

// for a `var` variable also add

//import androidx.compose.material.Tab
//import com.example.alxplair2.ui.theme.AlxPLair2Theme
import android.content.ContentValues
import android.os.Bundle
import android.os.PersistableBundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material.ExperimentalMaterialApi
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.lifecycleScope
import com.example.hobbyapp.ui.theme.HobbyAppTheme
import kotlinx.coroutines.launch


class MainActivity : ComponentActivity() {

    private val vm by viewModels<MainViewModel>()
    //val vm = MainViewModel()
    override fun onStop() {
        super.onStop()
        Log.e(ContentValues.TAG, "mqtt onStop")
        lifecycleScope.launch {

            vm.mqtt.client.disconnect()
        }
    }

    override fun onStart() {
        super.onStart()

        Log.e(ContentValues.TAG, "mqtt onStart")

        //var myJson = "{\"caca\":\"50\"}"
//        vm.init()
//        vm.mqtt.Connect()
//        vm.mqtt.requestStatuses()

        //var parsed:JSONObject = JSONObject(myJson) //= JSON.parse(Room.serializer())
        //var res = parsed.put("test",20)
        //var result = parsed.getJSONObject(myJson)
        //println("mqtt json ${parsed.getString("caca")}")
//        for (key in parsed.keys()) {
//            println("mqtt json ${key}")
//        }
        //val workData = workDataOf("ACTION" to "INIT")

//        WorkManager.getInstance(application)
//            .beginWith(OneTimeWorkRequestBuilder<MqttWorker>()
//                .setInputData(
//                    workDataOf("ACTION" to "INIT"))
//                .build())
//            .then(OneTimeWorkRequestBuilder<MqttWorker>()
//                .setInputData(
//                    workDataOf("ACTION" to "REFRESH"))
//                .build())
//            .enqueue()



//        workManager.enqueue(OneTimeWorkRequestBuilder<MqttWorker>()
//            //.setInitialDelay(1,TimeUnit.SECONDS)
//            .setInputData(workData)
//
//            .build())


        lifecycleScope.launch {
            //vm.init()
            //vm.refresh()
        //workManager.enqueue(OneTimeWorkRequest.from(MqttWorker::class.java))

            setContent {
                HobbyAppTheme {

//                var signInRequest = BeginSignInRequest.builder()
//                    .setGoogleIdTokenRequestOptions(
//                        BeginSignInRequest.GoogleIdTokenRequestOptions.builder()
//                            .setSupported(true)
//                            // Your server's client ID, not your Android client ID.
//                            .setServerClientId(getString(R.string.your_web_client_id))
//                            // Only show accounts previously used to sign in.
//                            .setFilterByAuthorizedAccounts(true)
//                            .build())
//                    .


                      PageContent()
//                    Box(
//                        modifier = Modifier
//                            .fillMaxSize()
//                            .background(color = Color.DarkGray)
//                            .padding(all = 0.dp)
//                    ) {
//                        Tab1()
//                    }
                }

            }
        }

//        vm.init()
//
    }

    @Preview
    @Composable
    fun preview() {
        //var vm = MainViewModel()
        //Text(text = "caca", color = Color.White)
        //CardBirou2(room = Room(), mainViewModel = vm)
    }


    override fun onCreate(savedInstanceState: Bundle?, persistentState: PersistableBundle?) {
        super.onCreate(savedInstanceState, persistentState)
        Log.e(ContentValues.TAG, "mqtt onCreate")

    }

    @OptIn(ExperimentalMaterialApi::class)
    @Composable
    fun PageContent() {
        val clicked = remember { mutableStateOf(0) }
        val selectedTab = remember { mutableStateOf(0) }

        //mainViewModel.onUpdate.value
        println("mqtt render Pagecontent")

        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(color = Color.DarkGray)
                .padding(all = 0.dp)
        ) {

            Column(
                modifier = Modifier
                    .padding(0.dp)
                    .fillMaxSize()
                    .background(Color.Black),
            ) {
                TabRow(
                    selectedTabIndex = selectedTab.value,
                    containerColor = Color.DarkGray,
                    modifier = Modifier
                        .height(30.dp),
                    //.clip(RoundedCornerShape(10.dp))
                    contentColor = Color.Gray

                ) {


                    Tab(
                        selected = selectedTab.value == 0,
                        onClick = {
                            clicked.value = 1
                            selectedTab.value = 0

                        },
                    ) {
                        Text(
                            text = "Ambient",
                            color = Color.White
                        )

                    }
                    Tab(
                        selected = selectedTab.value == 1,
                        onClick = {
                            clicked.value = 2
                            selectedTab.value = 1

                        },//, modifier = Modifier.absolutePadding(left = 30.dp)
                        modifier = Modifier.background(Color.DarkGray)
                    ) {
                        Text(
                            //modifier = Modifier.background(Color.White),
                            text = "Altele",
                            color = Color.White
                        )

                    }

                    Tab(
                        selected = selectedTab.value == 2,
                        onClick = {
                            clicked.value = 3
                            selectedTab.value = 2

                        },//, modifier = Modifier.absolutePadding(left = 30.dp)
                        modifier = Modifier.background(Color.DarkGray)
                    ) {
                        Text(
                            //modifier = Modifier.background(Color.White),
                            text = "Not Used",
                            color = Color.White
                        )

                    }
                }

                Spacer(modifier = Modifier.padding(10.dp))

                Row(modifier = Modifier.fillMaxWidth()) {
                    //Image(painter= painterResource(id = androidx.core.R.drawable.notification_template_icon_bg),"test")
                    Column {
                        //Text(modifier = Modifier.background(Color.Gray), text = "Text 1")
                        //Text(modifier = Modifier.background(Color.LightGray), text = "Text 2")
                        when (selectedTab.value) {

                            0 -> Tab1()
                            1 -> show2()
                            2 -> show3()

                        }
                    }

                }

            }
        }

    }


}


