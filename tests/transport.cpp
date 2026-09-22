// Host simulation compiles the real component against minimal ESPHome/UART doubles.
#include "esppac.cpp"
#include "esppac_cnt.cpp"
#include <cassert>
#include <iostream>
using namespace esphome;
using namespace esphome::sinclair_ac;
using namespace esphome::sinclair_ac::CNT;
struct AC : SinclairACCNT {
 bool ready(){return state_==ACState::Ready;}
 unsigned retries(){return retries_;} unsigned invalid(){return invalid_frames_;}
 unsigned partial(){return partial_resets_;}
 bool pending(){return update_!=ACUpdate::NoUpdate;}
 void feed(std::vector<uint8_t> p){rx.insert(rx.end(),p.begin(),p.end());loop();}
};
std::vector<uint8_t> report(){
 // Captured bathroom 0x30/0x31 frame, actual room 19 C, target 25 C.
 std::vector<uint8_t> p(51,0);p[0]=p[1]=0x7e;p[2]=0x30;p[3]=0x31;
 p[6]=0x40;p[8]=0x21;p[9]=0x90;p[10]=p[11]=2;p[22]=1;p[46]=0x3b;
 uint8_t c=0;for(size_t i=2;i+1<p.size();i++)c+=p[i];p.back()=c;return p;
}
void passive(const std::vector<uint8_t>&p){
 assert(p.size()==50 && p[2]==0x2f && p[3]==1);
 assert(p[15]&8); // protocol no-change flag
 assert(p[7]!=0xaf); // no update command
 uint8_t sum=0;for(size_t i=2;i+1<p.size();i++)sum+=p[i];assert(sum==p.back());
}
int main(){
 clock_ms=0;AC ac;ac.setup();clock_ms=1999;ac.loop();assert(ac.tx.empty());
 clock_ms=2000;ac.loop();assert(ac.tx.size()==1);passive(ac.tx.back());
 clock_ms=3999;ac.loop();assert(ac.tx.size()==1);
 clock_ms=4000;ac.loop();assert(ac.tx.size()==2&&ac.retries()==1);passive(ac.tx.back());
 for(int i=0;i<15;i++){clock_ms+=2000;ac.loop();passive(ac.tx.back());}
 assert(ac.tx.size()==17); // repeated silence never deadlocks
 ac.feed(report());assert(ac.ready());assert(ac.current_temperature==19&&ac.target_temperature==25);
 climate::ClimateCall call;call.requested_mode=climate::CLIMATE_MODE_DRY;ac.control(call);
 clock_ms+=300;ac.loop();assert(!(ac.tx.back()[15]&8));assert(ac.tx.back()[7]==0xaf);
 clock_ms+=1000;ac.loop();assert(!ac.ready()&&!ac.pending());
 clock_ms+=1000;ac.loop();passive(ac.tx.back());
 ac.control(call);assert(!ac.pending()); // reject offline control
 ac.feed(report());assert(ac.ready()&&ac.mode==climate::CLIMATE_MODE_OFF);
 clock_ms+=300;ac.loop();passive(ac.tx.back()); // cancelled dry must not be replayed
 auto bad=report();bad.back()^=1;ac.feed(bad);assert(ac.invalid()==1);
 clock_ms+=2000;ac.loop();assert(!ac.ready());passive(ac.tx.back());
 ac.feed({0x7e,0x7e,0x30,0x31,0});clock_ms+=251;ac.loop();assert(ac.partial()>0);
 ac.feed(report());assert(ac.ready());
 // Valid checksum but short payload must not reach the status decoder.
 ac.feed({0x7e,0x7e,2,0x31,0x33});assert(ac.invalid()==2);
 ac.feed({0x7e,0x7e,0xff});ac.feed(report());assert(ac.ready());
 // unsigned elapsed timing must survive millis() rollover.
 clock_ms=0xfffffc00u;AC wrap;wrap.setup();clock_ms+=2000;wrap.loop();assert(wrap.tx.size()==1);
 clock_ms+=2000;wrap.loop();assert(wrap.tx.size()==2&&wrap.retries()==1);
 std::cout<<"PASS: startup silence, repeated retries, captured report, dry command, lost response, no replay, offline rejection, corrupt/short/partial frames, resync, clock rollover\n";
}
