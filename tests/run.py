from pathlib import Path
import re, subprocess, tempfile
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp); src='\n'.join(f.read_text() for f in (root/'components/sinclair_ac').glob('*.cpp'))
 enums={k:sorted(set(re.findall(r'\b'+k+r'[A-Z_]+',src))) for k in ['CLIMATE_MODE_','CLIMATE_ACTION_','CLIMATE_SWING_']}
 stub='''#pragma once
#include <cstdint>
#include <vector>
#include <string>
#include <optional>
#include <deque>
#include <cmath>
#include <cstring>
#include <initializer_list>
#include <cstdio>
namespace esphome {
inline uint32_t clock_ms=0;
inline uint32_t millis(){return clock_ms;}
inline std::string format_hex_pretty(const std::vector<uint8_t>&){return "";}
struct Component{virtual void setup(){} virtual void loop(){} void status_clear_error(){} void status_set_error(){}};
namespace uart {struct UARTDevice {std::deque<uint8_t> rx; std::vector<std::vector<uint8_t>> tx;
int available(){return rx.size();} bool read_byte(uint8_t* c){if(rx.empty())return false;*c=rx.front();rx.pop_front();return true;}
void write_array(const std::vector<uint8_t>&p){tx.push_back(p);}};}
namespace sensor {struct Sensor{template<class F> void add_on_state_callback(F){}};}
namespace select {struct Option{std::string str(){return "";}};struct Select{Option current_option(){return {};}
std::optional<std::string> at(size_t){return std::string();} void publish_state(const std::string&){} template<class F>void add_on_state_callback(F){}};}
namespace switch_ {struct Switch{void publish_state(bool){} template<class F>void add_on_state_callback(F){}};}
namespace climate {
'''
 for prefix,name in [('CLIMATE_MODE_','ClimateMode'),('CLIMATE_ACTION_','ClimateAction'),('CLIMATE_SWING_','ClimateSwingMode')]:stub+='enum '+name+'{'+','.join(enums[prefix])+'};\n'
 stub+='''constexpr int CLIMATE_SUPPORTS_CURRENT_TEMPERATURE=1;
struct ClimateTraits{void set_feature_flags(int){} void set_visual_min_temperature(float){} void set_visual_max_temperature(float){} void set_visual_temperature_step(float){}
void set_supported_modes(std::initializer_list<ClimateMode>){} void set_supported_swing_modes(std::initializer_list<ClimateSwingMode>){} };
struct ClimateCall{std::optional<ClimateMode> requested_mode; std::optional<ClimateMode> get_mode()const{return requested_mode;}
std::optional<float> get_target_temperature()const{return {};} bool has_custom_fan_mode()const{return false;} std::string get_custom_fan_mode()const{return "";}
std::optional<ClimateSwingMode>get_swing_mode()const{return {};}};
struct Climate{ClimateMode mode=CLIMATE_MODE_OFF; ClimateSwingMode swing_mode=CLIMATE_SWING_OFF; ClimateAction action=CLIMATE_ACTION_OFF;
float current_temperature=NAN,target_temperature=NAN; std::string fan; int published=0;
virtual ClimateTraits traits(){return {};} virtual void control(const ClimateCall&){} void publish_state(){published++;}
void set_supported_custom_fan_modes(std::initializer_list<const char*> ){} bool has_custom_fan_mode(){return !fan.empty();}
std::string get_custom_fan_mode(){return fan;} void set_custom_fan_mode_(const std::string&s){fan=s;}};
}}
#define ESP_LOGV(...) do {} while(0)
#define ESP_LOGD(...) do {} while(0)
#define ESP_LOGI(tag,fmt,...) do {if(false)printf(fmt, ##__VA_ARGS__);}while(0)
#define ESP_LOGW(tag,fmt,...) do {if(false)printf(fmt, ##__VA_ARGS__);}while(0)
'''
 (p/'stub.h').write_text(stub)
 for f in ['core/log.h','core/component.h','components/climate/climate.h','components/climate/climate_mode.h','components/select/select.h','components/sensor/sensor.h','components/switch/switch.h','components/uart/uart.h']:
  target=p/'esphome'/f;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('#include "stub.h"\n')
 subprocess.run(['g++','-std=c++17','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-I'+str(p),'-I'+str(root/'components/sinclair_ac'),str(root/'tests/transport.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
