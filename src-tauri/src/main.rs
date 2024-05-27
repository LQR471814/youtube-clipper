#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use tauri::api::process::Command;

fn main() {
  Command::new_sidecar("server")
    .expect("failed to create binary command `server`")
    .spawn()
    .expect("failed to spawn sidecar");

    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
