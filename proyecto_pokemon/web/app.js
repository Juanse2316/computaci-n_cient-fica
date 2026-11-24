const $ = id => document.getElementById(id);
const colors = {Fuego:'#ff9775',Agua:'#78baff',Planta:'#9de19b','Eléctrico':'#f4d975',Hielo:'#8adedd',Lucha:'#f6a082',Veneno:'#cf99ee',Tierra:'#d9bc83',Volador:'#aabefa','Psíquico':'#fa9ec0',Bicho:'#c1d877',Roca:'#d1c399',Fantasma:'#b6a0ef','Dragón':'#a79cff',Siniestro:'#b9b1cb',Acero:'#adcad6',Hada:'#f3b2db',Normal:'#c5cbd3'};
let catalogo=[], seleccion=[], equipos=[], nombres=[], jugador=0, sesion=null, estado=null, ocupado=false;
let firmaRegistro='';
const escapeHTML = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const tipos = ts => `<div class="types">${ts.map(t=>`<span class="type">${escapeHTML(t)}</span>`).join('')}</div>`;
const imagen = nombre => `/imagenes/${encodeURIComponent(nombre.toLowerCase())}.png`;
const miniatura = nombre => `<img class="miniatura" src="${imagen(nombre)}" alt="" width="48" height="48" loading="lazy">`;
const avatar = (nombre,tipo) => `<div class="avatar" style="--accent:${colors[tipo]}"><img src="${imagen(nombre)}" alt="${escapeHTML(nombre)}" width="475" height="475" decoding="async"></div>`;
function error(e){$('error').textContent=e.message; $('error').hidden=false;}
async function api(ruta,datos){
  const respuesta=await fetch(ruta,datos?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(datos)}:{});
  const resultado=await respuesta.json();
  if(!respuesta.ok) throw new Error(resultado.error || 'No fue posible completar la acción.');
  return resultado;
}
function renderCatalogo(){
  const filtro=$('buscar').value.toLocaleLowerCase();
  $('catalogo').innerHTML=catalogo.filter(p=>`${p.nombre} ${p.tipo_1} ${p.tipo_2||''}`.toLocaleLowerCase().includes(filtro)).map(p=>{
    const elegido=seleccion.includes(p.id);
    return `<button class="poke-card ${elegido?'selected':''}" style="--accent:${colors[p.tipo_1]}" data-pokemon="${p.id}" aria-pressed="${elegido}" ${!elegido&&seleccion.length===3?'disabled':''}><span class="mark">${elegido?'✓':'+'}</span>${avatar(p.nombre,p.tipo_1)}<strong>${p.nombre}</strong>${tipos([p.tipo_1,p.tipo_2].filter(Boolean))}<span class="stat">HP ${p.estadisticas.hp} · VEL ${p.estadisticas.velocidad}</span></button>`;
  }).join('') || '<p>No hay Pokémon con ese nombre o tipo.</p>';
  $('contador').textContent=`${seleccion.length} / 3`;
  $('elegidos').innerHTML=Array.from({length:3},(_,i)=>`<div class="slot ${seleccion[i]?'filled':''}">${seleccion[i]?miniatura(catalogo.find(p=>p.id===seleccion[i]).nombre)+catalogo.find(p=>p.id===seleccion[i]).nombre:'Sin seleccionar'}</div>`).join('');
  $('confirmar').disabled=seleccion.length!==3 || ocupado;
}
$('buscar').addEventListener('input',renderCatalogo);
$('catalogo').addEventListener('click',e=>{
  const boton=e.target.closest('[data-pokemon]'); if(!boton || ocupado)return;
  const id=Number(boton.dataset.pokemon);
  seleccion=seleccion.includes(id)?seleccion.filter(x=>x!==id):[...seleccion,id].slice(0,3);
  renderCatalogo();
});
$('confirmar').addEventListener('click',async()=>{
  if(ocupado || seleccion.length!==3)return;
  equipos[jugador]=[...seleccion]; nombres[jugador]=$('nombre').value.trim()||`Jugador ${jugador+1}`;
  if(jugador===0){
    jugador=1; seleccion=[]; $('nombre').value='Jugador 2'; $('buscar').value='';
    $('paso').textContent='PREPARACIÓN · JUGADOR 2'; $('confirmar').textContent='Comenzar batalla'; renderCatalogo(); $('nombre').focus(); return;
  }
  ocupado=true; renderCatalogo(); $('error').hidden=true;
  try{
    const data=await api('/api/iniciar',{equipos,nombres,sesion}); sesion=data.sesion; estado=data.estado;
    $('seleccion').hidden=true; $('combate').hidden=false; $('registro').innerHTML='<p>¡Los equipos están listos! Comienza la batalla.</p>'; firmaRegistro=''; renderBatalla();
  }catch(e){error(e);}finally{ocupado=false; renderCatalogo();}
});
function renderBatalla(){
  $('turno').textContent=`TURNO ${estado.turno}`;
  estado.jugadores.forEach((j,i)=>{
    const p=j.equipo.find(p=>p.activo), porcentaje=Math.round(p.hp/p.max*100);
    $(`lado${i}`).innerHTML=`<span class="trainer">${escapeHTML(j.nombre)}</span>${avatar(p.nombre,p.tipos[0])}<h2>${p.nombre}</h2>${tipos(p.tipos)}<div class="hp-row"><span>VIDA ${porcentaje}%</span><span>${p.hp} / ${p.max} HP</span></div><div class="hp-track" role="progressbar" aria-label="Vida de ${p.nombre}" aria-valuenow="${p.hp}" aria-valuemin="0" aria-valuemax="${p.max}"><div class="hp-fill" style="width:${porcentaje}%;background:${porcentaje<25?'#ff858a':porcentaje<50?'#ffd478':'#d8fc73'}"></div></div><div class="team">${j.equipo.map(p=>`<span class="${p.activo?'active':''} ${!p.hp?'fainted':''}">${miniatura(p.nombre)}${p.nombre}${!p.hp?' · KO':''}</span>`).join('')}</div>`;
  });
  const firma=JSON.stringify([estado.turno,estado.eventos]);
  if(estado.eventos.length && firma!==firmaRegistro){
    $('registro').innerHTML=estado.eventos.map(e=>`<p>${escapeHTML(e)}</p>`).join(''); firmaRegistro=firma;
  }
  if(estado.ganador!==null){
    $('fase').textContent='BATALLA FINALIZADA'; $('instruccion').textContent=estado.ganador==='Empate'?'¡Empate!':`¡Victoria de ${estado.ganador}!`;
    $('ayuda').textContent='Puedes iniciar otra partida y probar una nueva combinación de equipos.'; $('acciones').innerHTML=''; return;
  }
  const j=estado.jugadores[estado.elige], p=j.equipo.find(p=>p.activo);
  $('fase').textContent=estado.reemplazo?'REEMPLAZO OBLIGATORIO':`COMANDOS · JUGADOR ${estado.elige+1}`;
  $('instruccion').textContent=`${j.nombre}, ${estado.reemplazo?'elige tu reemplazo.':'elige tu acción.'}`;
  $('ayuda').textContent=estado.reemplazo?'Tu Pokémon se debilitó. Elige una reserva para continuar.':estado.elige===1?'La primera acción está guardada. Entrega el control al segundo jugador.':'Ambos eligen su acción antes de resolver el turno. Los cambios tienen prioridad.';
  let contenido='';
  if(!estado.reemplazo){
    contenido='<div class="moves">'+p.movimientos.map((m,i)=>`<button class="move" data-tipo="atacar" data-indice="${i}" ${!m.pp?'disabled':''}><strong>${m.nombre}</strong><small>${m.tipo} · ${m.categoria}</small><small>Pot. ${m.potencia} · Prec. ${m.precision}% · PP ${m.pp}/${m.max}</small></button>`).join('')+'</div>';
    if(p.movimientos.every(m=>!m.pp))contenido+='<button class="primary" data-tipo="forcejeo" data-indice="0">Forcejeo · con retroceso</button>';
  }
  const reservas=j.equipo.map((p,i)=>({p,i})).filter(({p})=>!p.activo&&p.hp>0);
  if(reservas.length)contenido+=`<div class="reserves">${reservas.map(({p,i})=>`<button class="secondary" data-tipo="${estado.reemplazo?'reemplazar':'cambiar'}" data-indice="${i}">${miniatura(p.nombre)}${estado.reemplazo?'Enviar':'Cambiar a'} ${p.nombre} · ${p.hp} HP</button>`).join('')}</div>`;
  $('acciones').innerHTML=contenido;
}
$('acciones').addEventListener('click',async e=>{
  const boton=e.target.closest('[data-tipo]'); if(!boton||ocupado)return;
  ocupado=true; $('error').hidden=true; $('acciones').querySelectorAll('button').forEach(b=>b.disabled=true);
  $('reiniciar').disabled=true;
  try{
    const data=await api('/api/accion',{sesion,tipo:boton.dataset.tipo,indice:Number(boton.dataset.indice)});
    await reproducirTurno(data.animaciones || []);
    estado=data.estado;
  }
  catch(e){error(e);}finally{ocupado=false;$('reiniciar').disabled=false;renderBatalla();$('instruccion').focus();}
});
const esperar = ms => new Promise(resolve=>setTimeout(resolve,ms));
const movimientoReducido = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
function animarVida(lado, anterior, actual, maximo){
  const barra=lado.querySelector('.hp-fill'), pista=lado.querySelector('.hp-track');
  const etiquetas=lado.querySelectorAll('.hp-row span');
  const duracion=movimientoReducido()?0:900;
  barra.style.transition='none';
  return new Promise(resolve=>{
    const inicio=performance.now();
    function pintar(ahora){
      const progreso=duracion?Math.min(1,(ahora-inicio)/duracion):1;
      const hp=Math.round(anterior+(actual-anterior)*(1-Math.pow(1-progreso,3)));
      const porcentaje=hp/maximo*100;
      barra.style.width=`${porcentaje}%`;
      barra.style.background=porcentaje<25?'#ff858a':porcentaje<50?'#ffd478':'#d8fc73';
      etiquetas[0].textContent=`VIDA ${Math.round(porcentaje)}%`;
      etiquetas[1].textContent=`${hp} / ${maximo} HP`;
      pista.setAttribute('aria-valuenow',hp);
      if(progreso<1)requestAnimationFrame(pintar);else resolve();
    }
    pintar(inicio);
  });
}
async function reproducirTurno(pasos){
  for(const paso of pasos){
    const anteriores=estado.jugadores.map(j=>({...j.equipo.find(p=>p.activo)}));
    if(paso.tipo!=='cambiar'&&!movimientoReducido()){
      const atacante=$(`lado${paso.actor}`).querySelector('.avatar');
      atacante.classList.add(paso.actor===0?'ataca-derecha':'ataca-izquierda');
      await esperar(300);
      atacante.classList.remove('ataca-derecha','ataca-izquierda');
    }
    paso.activos.forEach((activo,i)=>{
      estado.jugadores[i].equipo.forEach(p=>{
        p.activo=p.nombre===activo.nombre;
        if(p.activo)p.hp=activo.hp;
      });
    });
    estado.eventos=paso.eventos;
    renderBatalla();
    $('fase').textContent='RESOLVIENDO TURNO';
    $('instruccion').textContent=paso.tipo==='cambiar'?'Cambio de Pokémon':'¡Ataque en curso!';
    $('ayuda').textContent='Espera a que terminen las acciones del turno.';
    $('acciones').querySelectorAll('button').forEach(b=>b.disabled=true);
    const efectos=paso.activos.map(async(actual,i)=>{
      const lado=$(`lado${i}`), previo=anteriores[i];
      if(previo.nombre!==actual.nombre){
        lado.querySelector('.avatar').classList.add('entrada-pokemon');
        return;
      }
      const daño=previo.hp-actual.hp;
      if(daño<=0)return;
      const numero=document.createElement('span');
      numero.className='daño-flotante'; numero.textContent=`−${daño} HP`;
      lado.querySelector('.avatar').append(numero);
      lado.querySelector('.avatar img').classList.add('recibe-golpe');
      await animarVida(lado,previo.hp,actual.hp,previo.max);
      if(actual.hp===0)lado.querySelector('.avatar img').classList.add('cae-debilitado');
    });
    await Promise.all(efectos);
    await esperar(movimientoReducido()?150:650);
  }
}
$('reiniciar').addEventListener('click',()=>{
  if(ocupado)return;
  if(estado.ganador===null&&!confirm('¿Terminar esta batalla y elegir nuevos equipos?'))return;
  jugador=0; seleccion=[]; equipos=[]; nombres=[]; estado=null;
  $('seleccion').hidden=false; $('combate').hidden=true; $('nombre').value='Jugador 1'; $('buscar').value='';
  $('paso').textContent='PREPARACIÓN · JUGADOR 1'; $('confirmar').textContent='Confirmar equipo'; $('error').hidden=true; renderCatalogo();
});
api('/api/catalogo').then(data=>{catalogo=data;renderCatalogo();}).catch(error);
