// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::Command;

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![run_python_script])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}


#[tauri::command]
fn run_python_script(param1: String, param2: String, param3: String, param4: String, param5: String) -> Result<String, String> {
    let output = Command::new("python3")
        .arg("python/geopy.py")
        .args([ &param1, &param2, &param3, &param4, &param5])
        .output();
    println!("Rust activated");

    match output {
        Ok(output) => Ok(String::from_utf8_lossy(&output.stdout).to_string()),
        Err(e) => Err(e.to_string()),
    }
}
