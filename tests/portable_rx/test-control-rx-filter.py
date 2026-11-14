from pathlib import Path
import subprocess,tempfile
T=Path(__file__).resolve().parent;R=T.parents[1];s=(R/'itlwm/hal_iwx/ItlIwx.cpp').read_text()
def part(a,b):return s[s.index(a):s.index(b,s.index(a))]
method='int ItlIwx::\n'+part('awdlCoexMacSend(struct iwx_softc','\n// The listener')
a=s.index('    if (filterChange) {',s.index('awdlCoexBaHandle(struct'));b=a+len('    if (filterChange) {');depth=1
while depth:depth+=(s[b]=='{')-(s[b]=='}');b+=1
restore=s[a:b]
force=part('    const bool controlRxWanted =','    if (filterChange) {')
caller='struct { bool off=false; } awdlCoexBaFilter; static unsigned awdlCoexBaFilterChanges;\nvoid ItlIwx::runFilterChange(iwx_softc *sc,bool wanted,bool always){const bool filterWasOff=awdlCoexBaFilterOff;bool filterChange=always||wanted!=filterWasOff;awdlCoexBaFilter.off=wanted;const int gen=sc->sc_generation;auto stillOurs=[&](){return gen==sc->sc_generation;};\n'+force+restore+'\n}\n'
p=r'''

#include <cassert>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <initializer_list>
static uint32_t htole32(uint32_t x){return x;}
#define IEEE80211_ADDR_COPY(a,b) memcpy(a,b,6)
#define IWX_FW_CMD_ID_AND_COLOR(a,b) ((a)|((b)<<8))
#define IEEE80211_IS_CHAN_2GHZ(p) ((p)->number<15)
struct ieee80211_channel { unsigned number=149; };
struct Phy { ieee80211_channel *channel=nullptr; };
struct ieee80211_node { Phy *in_phyctxt=nullptr; };
struct iwx_node { Phy *in_phyctxt=nullptr; };
struct ieee80211com { ieee80211_node *ic_bss=nullptr; uint8_t ic_myaddr[6]={0,1,2,3,4,5}; };
struct iwx_softc { ieee80211com sc_ic; int sc_generation=1; };
static unsigned ieee80211_chan2ieee(ieee80211com*,const ieee80211_channel *p){return p->number;}
struct iwx_mac_ctx_cmd { uint32_t id_and_color,action,mac_type,tsf_id; uint8_t node_addr[6],bssid_addr[6];uint32_t cck_rates,ofdm_rates,filter_flags; };
enum { IWX_FW_CTXT_ACTION_ADD=1,IWX_FW_CTXT_ACTION_MODIFY=2,IWX_FW_CTXT_ACTION_REMOVE=3,IWX_FW_MAC_TYPE_LISTENER=4,IWX_TSF_ID_B=1,IWX_MAC_CONTEXT_CMD=77,kAwdlCoexMacId=1,kCoexBaTxAsking=1,kCoexBaTxAgreed=2 };
enum { IWX_MAC_FILTER_IN_PROMISC=1,IWX_MAC_FILTER_IN_CONTROL_AND_MGMT=2,IWX_MAC_FILTER_ACCEPT_GRP=4,IWX_MAC_FILTER_IN_BEACON=64,IWX_MAC_FILTER_IN_PROBE_REQUEST=4096 };
static bool awdlCoexAddrKnown=true,awdlCoexBaFilterOff=false,awdlCoexBaTxEnabled=true,awdlCoexPromiscLive=false,awdlCoexPromiscUncertain=false,awdlCoexBaPeerAdded=true;
static uint32_t awdlCoexToken=1;static unsigned awdlCoexFilter=3;static uint8_t awdlCoexBaTids=1;static int awdlCoexBaTxState=kCoexBaTxAsking;
static uint8_t awdlCoexAddr[6]={2,1,2,3,4,6},etherbroadcastaddr[6]={255,255,255,255,255,255};
static ieee80211_channel own;static ieee80211_channel *awdlCoexOwnChan=&own;
static bool awdlCoexControlRxLive;
static uint64_t nowUS=1000000,awdlCoexBaProbeUntilUS=1250000;
static uint64_t awdlUptimeUS(){return nowUS;}
static void iwx_ack_rates(iwx_softc*,iwx_node*,int *cck,int *ofdm){*cck=15;*ofdm=21;}
static int injected; static iwx_mac_ctx_cmd submitted;
static bool controlWantedFlag=false,awdlCoexControlRxRestorePending=false;
static uint64_t controlDeadline=0;
static bool awdlControlReceiveProbeWanted(iwx_softc*,uint64_t now){return controlWantedFlag&&now<controlDeadline;}
class ItlIwx {public:int awdlCoexMacSend(iwx_softc*,uint32_t);int baselineMacSend(iwx_softc*,uint32_t);void runFilterChange(iwx_softc*,bool,bool);int iwx_send_cmd_pdu(iwx_softc *s,int id,int flags,unsigned size,void *cmd){assert(id==IWX_MAC_CONTEXT_CMD && !flags && size==sizeof(iwx_mac_ctx_cmd));submitted=*static_cast<iwx_mac_ctx_cmd*>(cmd);if(injected==2)++s->sc_generation;if(injected==3)++awdlCoexToken;return injected==1?5:0;}};

''' + method + caller + r'''

int main(){iwx_softc sc;ItlIwx driver;Phy phy;ieee80211_node node;ieee80211_channel station;phy.channel=&station;node.in_phyctxt=&phy;sc.sc_ic.ic_bss=&node;
 unsigned cases=0;
 auto reset=[&](){injected=0;nowUS=1000000;awdlCoexFilter=3;awdlCoexBaFilterOff=false;awdlCoexControlRxLive=false;awdlCoexControlRxRestorePending=false;controlWantedFlag=true;controlDeadline=1250000;};
 for(bool failOpen:{false,true})for(bool failClose:{false,true}){reset();injected=failOpen?1:0;driver.awdlCoexMacSend(&sc,2);assert(awdlCoexControlRxRestorePending);assert(awdlCoexControlRxLive==!failOpen);nowUS=controlDeadline;injected=failClose?1:0;driver.runFilterChange(&sc,false,false);assert(awdlCoexControlRxRestorePending==failClose);if(failClose){injected=0;driver.runFilterChange(&sc,false,false);}assert(!awdlCoexControlRxLive&&!awdlCoexControlRxRestorePending);++cases;}
 for(int failure:{2,3}){reset();injected=failure;driver.awdlCoexMacSend(&sc,2);assert(!awdlCoexControlRxLive&&awdlCoexControlRxRestorePending);nowUS=controlDeadline;injected=0;driver.runFilterChange(&sc,false,false);assert(!awdlCoexControlRxRestorePending);++cases;}
 for(bool oldOff:{false,true})for(bool wanted:{false,true})for(bool always:{false,true})for(bool fail:{false,true}){reset();controlWantedFlag=false;awdlCoexBaFilterOff=oldOff;injected=fail?1:0;driver.runFilterChange(&sc,wanted,always);assert(awdlCoexBaFilterOff==(fail?oldOff:wanted));assert(awdlCoexBaFilter.off==awdlCoexBaFilterOff);++cases;}
 printf("PASS %u production control-window failed-open/failed-close/retry/token/generation/rollback cases\n",cases);
}

'''
with tempfile.TemporaryDirectory() as d:
 c=Path(d)/'check.cpp';c.write_text(p);exe=Path(d)/'check';subprocess.run(['xcrun','clang++','-std=c++14','-fsanitize=address,undefined',str(c),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
