package com.example.hobbyapp

import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun show2(vm: MainViewModel = viewModel()) {
    Text(text = "222222222222", color = Color.Green)
}