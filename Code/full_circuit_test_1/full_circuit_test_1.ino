/*
   TESTE 1 DO CIRCUITO COMPLETO (LÓGICA + POTÊNCIA)
   Objetivo: colocar a pilha de piezos em ciclo de carga e descarga a 45 V.

   FASE 0: INICIALIZAÇÃO
   Placa energizada. D18 e D19 desligados: O1 e O2 desligados.

   Tempo de espera para inicialização: t0 = 50 μs

   FASE 1: CARREGAMENTO DO CAPACITOR DE BOOTSTRAP C1
   O2 conecta o gate e o source de Q1 ao GND, impedindo Q1 de ligar e causar um curto na linha de 200 V.
   O1 liga Q2, conectando o capacitor de bootstrap C1 ao referencial de 0 V (GND), carregando-o.
   Por segurança, O2 é ligado primeiro. Após um intervalo de segurnça, O1 é ligado.
   
   Tempo ativo de apenas D19: t1 = tON + td = 10 μs
      Tempo de acionamento do TLP627 O2 (turn-on time): tON = 5 μs
      Intervalo de segurança (dead time): td = 5 μs
   
   Tempo ativo de D18 e D19: t2 = tON + tm = 10 μs
      Tempo de acionamento do TLP627 O1 (turn-on time): tON = 5 μs
      Intervalo de margem: tm = 5 μs
      
   Obs.: O tempo de atraso no desligamento do TLP627 é grande o suficiente para carregar C1 mesmo que os
   optoacopladores fiquem ligados por apenas 5 μs (ts > tC1).
      Tempo de atraso no desligamento do TLP627 (storage time): ts = 40 μs
      Tempo de carga do capacitor de bootstrap C1: tC1 = 5 x RC1 x C1 = 7,5 μs
          Capacitância de C1: C1 = 1 μF
          Resistência do circuito de carga de C1: RC1 ≈ 1,5 Ω
              Resistência do N-MOSFET IRF740: Rm ≈ 0,6 Ω
              Resistência do diodo UF4007 em condução: Rd ≈ 0,5 Ω
              Resistência interna da fonte: Rf ≈ 0,1 Ω
              Resistência interna do capacitor: Rc ≈ 0,2 Ω

   Tempo ativo de apenas D19: t3 = ts + td = 50 μs
      Tempo de atraso no desligamento do TLP627 O1 (storage time): ts = 40 μs
      Intervalo de segurança (dead time): td = 10 μs
   
   FASE 2: CARREGAMENTO DOS PIEZOS
   C1 começa a carregar o gate de Q1 em relação ao source (V_GS). Após V_GS = 3 V, Q1 liga e começa a conduzir
   em regime resistivo do dreno para o source. A elevação da tensão no source faz com que a referência de C1
   flutue, mantendo a carga do gate até V_GS = 12 V, na qual Q1 conduz em regime não-resistivo até completar
   a carga da pilha de piezos.
   
   Obs.: Como a capacitância de C1 (1 μF) é mais de 700 vezes maior que a do gate de Q1, considera-se que a tensão
   entre os terminais de C1 se mantenha inalterada em 12 V.
   
   Tempo inativo de D18 e D19: t4 = tOFF + tGQ1 + tp + tm = 850 μs
      Tempo de desligamento do TLP627 O2 (turn-off time): tOFF = 80 μs
      Tempo de carga do gate de Q1: tGQ1 = 5 x RGQ1 x CGQ1 = 7,5 μs
          Resistência do circuito de carga do gate de Q1: RGQ1 = 1 kΩ
          Capacitância do gate de Q1: CGQ1 = 1,5 nF
      Tempo de carga da pilha de piezos: tp = 1,3 x (5 x Rp x Cp) = 747,5 μs (incerteza de 30% sobre valor de Cp)
          Capacitância medida da pilha: Cp ≈ 11,5 nF
          Resistência do circuito de carga da pilha: Rp = 10 kΩ
      Intervalo de margem: tm = 15 μs
   
   FASE 3: RETENÇÃO DE CARGA NOS PIEZOS
   O2 conecta o gate e o source de Q1, levando-os ao mesmo potencial e desligando Q1.
   A pilha de piezos segura a tensão entre seus terminais.

   Tempo ativo de D19: t5 = tON + tdGQ1 + tm = 10 μs
      Tempo de acionamento do TLP627 (turn-on time): tON = 5 μs
      Tempo de descarga do gate de Q1: tdGQ1 = 5 x RdGQ1 x CGQ1 = 3,75 μs
          Resistência do circuito de descarga do gate de Q1: RdGQ1 ≈ 500 Ω
          Capacitância do gate de Q1: CGQ1 = 1,5 nF
      Intervalo de margem: tm = 1,25 μs
   
   Obs.: O tempo total em que O2 fica ligado, considerando o tempo de atraso no desligamento do TLP627, é t5 - tON
   + ts = 45 μs. Durante esse tempo, os terminais de C1 estão conectados através dos resistores de 1 kΩ e 10 kΩ,
   levando a uma tensão V = 12 V x exp[(-45 μs / (C1 x 11 kΩ)] = 11,95 V = 99,6% x 12 V.
   
   Tempo inativo de D19: t6 = ts + tr = 140 μs
      Tempo de atraso no desligamento do TLP627 (storage time): ts = 40 μs
      Intervalo de retenção de carga: tr = 100 μs
      
   Obs.: Com O2 desligado na fase 3, os piezos seguram sua carga durante o intervalo tr. Esse intervalo pode ser
   ajustado livremente, conforme seja interessante para o sistema de controle.

   FASE 4: DESCARGA DOS PIEZOS
   Para a descarga dos piezos, O1 e O2 devem estar ligados juntos. Porém, se O1 abrir sozinho, a fonte carregará o
   gate de Q1 a 12 V, ligando-o e gerando um curto da linha de 200 V direto para o GND. Assim, por segurança, O2
   deve ligar primeiro, conectando o gate e o source de Q1 ao mesmo potencial, para que em seguida O1 conecte-os
   ao GND.

   Tempo ativo de D19: t7 = tON + td = 10 μs
      Tempo de acionamento do TLP627 O2 (turn-on time): tON = 5 μs
      Intervalo de segurança (dead time): td = 5 μs
   
   Tempo ativo de D18 e D19: t8 = tON + tdp - ts + tm = 740 μs
      Tempo de acionamento do TLP627 O1 (turn-on time): tON = 5 μs
      Tempo de descarga da pilha de piezos: tdp = 1,3 x (5 x Rdp x Cp) = 747,5 μs (incerteza de 30% sobre valor de Cp)
          Capacitância medida da pilha: Cp ≈ 11,5 nF
          Resistência do circuito de descarga da pilha: Rdp = 10 kΩ
      Tempo de atraso no desligamento do TLP627 O1 (storage time): ts = 40 μs
      Intervalo de margem: tm = 27,5 μs

   Tempo ativo de apenas D19: t9 = ts + td = 50 μs
      Tempo de atraso no desligamento do TLP627 O1 (storage time): ts = 40 μs
      Intervalo de segurança (dead time): td = 10 μs
   
   Obs.: O tempo de descarga dos piezos é suficiente para recarregar C1 caso fosse necessário. A partir de então, o
   processo de carga e descarga pode entrar em ciclo entre as fases 2, 3 e 4.

   Obs.: O encerramento do programa deve se dar no meio da fase 4, com O1 e O2 ligados.
   
   RESUMO
   Período do teste: T = 1800 μs = 1,8 ms
   Frequência do teste: f = 555,5 Hz
*/

// Definição dos pinos
const int pin_o1 = 18; // Controle do optoacoplador O1
const int pin_o2 = 19; // Controle do optoacoplador O2

// Tempos-chave (μs)
const unsigned long t0 = 50;
const unsigned long t1 = 10;
const unsigned long t2 = 10;
const unsigned long t3 = 50;
const unsigned long t4 = 850;
const unsigned long t5 = 10;
const unsigned long t6 = 140;
const unsigned long t7 = 10;
const unsigned long t8 = 740;

// Número de ciclos antes do encerramento
const unsigned long numeroCiclos = 66667; // 66.667 ciclos x 1,8 ms = 120 s

void setup() {
  // Configuração dos pinos de controle como saída digital
  pinMode(pin_o1, OUTPUT);
  pinMode(pin_o2, OUTPUT);

  // Fase 0: Pinos de controle desligados
  digitalWrite(pin_o1, LOW);
  digitalWrite(pin_o2, LOW);
  delay(2000); // Pequena estabilização após energizar o microcontrolador

  // Fase 1: Carregamento de C1
  digitalWrite(pin_o2, HIGH); // Liga O2 primeiro por segurança
  delayMicroseconds(t1);      // Aguarda tempo de acionamento de O2 + intervalo de segurança
  digitalWrite(pin_o1, HIGH); // Liga O1 para conectar C1 ao GND
  delayMicroseconds(t2);      // Mantém O1 e O2 ligados durante carregamento de C1
}

void loop() {
  // ==========================================================================
  // Ciclo contínuo entre as fases 2, 3 e 4 (período total: 1800 us)
  // ==========================================================================

  for (unsigned long ciclo = 0; ciclo < numeroCiclos; ciclo++) {
   
   // Fase 2: Carregamento dos piezos
   digitalWrite(pin_o1, LOW);  // Desliga O1 primeiro para isolar circuito de bootstrap do GND
   delayMicroseconds(t3);      // Aguarda desligamento completo de O1 
   digitalWrite(pin_o2, LOW);  // Desliga O2 para ligar Q1
   delayMicroseconds(t4);      // Carregamento dos piezos

   // Fase 3: Retenção de carga nos piezos
   digitalWrite(pin_o2, HIGH); // Liga O2 para desligar Q1
   delayMicroseconds(t5);      // Aguarda o descarregmento do gate de Q1
   digitalWrite(pin_o2, LOW);  // Desliga O2 para abrir o circuito de bootstrap e não descarregar C1
   delayMicroseconds(t6);      // Retém a carga por tempo definido (t6 - 40 μs de atraso no desligamento de O2)

   // Fase 4: Descarga dos piezos
   digitalWrite(pin_o2, HIGH); // Liga O2 primeiro por segurança
   delayMicroseconds(t7);      // Aguarda tempo de acionamento de O2 + intervalo de segurança
   digitalWrite(pin_o1, HIGH); // Liga O1 para conectar o terminal positivo dos piezos ao GND
   delayMicroseconds(t8);      // Mantém O1 e O2 ligados durante descarga dos piezos
  }

  // Encerramento seguro após o número de ciclos definido
  digitalWrite(pin_o1, HIGH);
  digitalWrite(pin_o2, HIGH);

  while (true) {
   // Trava o programa com O1 e O2 ligados até a placa se desligada
  }
}