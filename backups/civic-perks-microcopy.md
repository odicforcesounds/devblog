# Civic Perks — in-app microcopy

Internal working note for the author. Not published, not linked from `docs/`.
Companion to `backups/civic-perks-usability.md`. Strings for the moments where the rules
currently read like operator notes: the auto-verify flag, the daily cap, Vanguard, the empty
map, permission, confirmation and moderation.

**Voice rules.** Second person, present tense, under 20 words where possible. No blame, no
exclamation marks, no "oops", no "unfortunately". Say what works before what waits. Every
number in local time. Keep the same keys across PT/EN/ES/FR; the Portuguese column is the
author's, the other two need a native pass.

## 1. First visit and sign-in

| Key | English | Português | Where |
| --- | --- | --- | --- |
| `visitor.strip` | Sign in to pin, confirm and keep your XP. | Entra para marcar, confirmar e guardar o teu XP. | Inline strip, logged out |
| `visitor.dismiss` | Look around first | Ver primeiro | Same strip |
| `visitor.pin_cta` | Sign in to confirm this pin | Entra para confirmar este pino | Pin sheet, logged out |
| `signin.reason` | We use Google only to identify you. Your photos stay on the map. | Usamos o Google apenas para te identificar. As tuas fotos ficam no mapa. | Under the sign-in button |
| `signin.guest_merge` | You have 3 pins waiting. Attach them to your account? | Tens 3 pinos à espera. Queres associá-los à tua conta? | After sign-in |

## 2. Location permission

| Key | English | Português | Where |
| --- | --- | --- | --- |
| `geo.pre_title` | Before we ask your phone | Antes de pedirmos ao telemóvel | Pre-permission sheet |
| `geo.pre_body` | Civic Perks reads your position while you play, to place pins and check you are near the one you confirm. Your live position is never shown to other people. | O Civic Perks lê a tua posição enquanto jogas, para colocar pinos e verificar se estás perto do que confirmas. A tua posição em direto nunca é mostrada a outras pessoas. | Same sheet |
| `geo.allow` | Use my location | Usar a minha localização | Primary button |
| `geo.later` | Not now | Agora não | Secondary button |
| `geo.denied_title` | The map still works | O mapa continua a funcionar | Denied banner |
| `geo.denied_body` | Tap the map to place a pin. It will be marked unverified and earn less XP. To turn location back on: Chrome → site settings → Location; Safari → aA → Website Settings → Location. | Toca no mapa para colocar um pino. Fica marcado como não verificado e ganha menos XP. Para voltar a ativar: Chrome → definições do site → Localização; Safari → aA → Definições do site → Localização. | Denied banner |
| `geo.accuracy_warn` | Your position is accurate to about {metres} m. Move to an open spot if you can. | A tua posição tem cerca de {metres} m de precisão. Se puderes, vai para um espaço aberto. | Before publishing |
| `geo.moving` | You seem to be moving. Stop somewhere safe before reporting. | Pareces estar em movimento. Para num local seguro antes de reportar. | Moving warning |

## 3. The flag on a new pin

| Key | English | Português | Where |
| --- | --- | --- | --- |
| `pin.flag_badge` | New | Novo | Pin sheet |
| `pin.flag_title` | We accept it now | Aceitámos agora | First pin result |
| `pin.flag_body` | Your pin is live and marked new. When a neighbour confirms it, the mark goes and the normal XP follows. | O teu pino está no mapa e marcado como novo. Quando um vizinho o confirmar, a marca desaparece e o XP normal segue. | Same screen |
| `pin.flag_help` | Why new pins are flagged | Porque é que os pinos novos ficam marcados | Info link |

## 4. Daily cap

| Key | English | Português | Where |
| --- | --- | --- | --- |
| `cap.counter` | 18 of 20 pins left today | 18 de 20 pinos disponíveis hoje | Pin button area |
| `cap.reset` | Resets at {time} | Reinicia às {time} | Counter tooltip |
| `cap.reached_title` | That is 20 pins today | São 20 pinos hoje | When the cap is hit |
| `cap.reached_body` | The limit keeps one person from filling the map alone. It resets at {time}. Your drafts are safe. | O limite evita que uma pessoa encha o mapa sozinha. Reinicia às {time}. Os teus rascunhos ficam guardados. | Same screen |
| `cap.why` | Why a daily limit | Porque existe um limite diário | Info link |

## 5. Vanguard (fewer than three scouts)

| Key | English | Português | Where |
| --- | --- | --- | --- |
| `vanguard.badge` | First scout | Primeiro explorador | Area header |
| `vanguard.title` | You are the first one here | És o primeiro aqui | Vanguard panel |
| `vanguard.body` | Walking, reporting and quests still work. Validation and solving open when a third scout joins. | Caminhar, reportar e as missões continuam a funcionar. A validação e a resolução abrem quando chegar um terceiro explorador. | Same panel |
| `vanguard.progress` | {count} of 3 scouts here | {count} de 3 exploradores aqui | Progress line |
| `vanguard.credits` | Credits stay flat until the area has three scouts, so nobody earns more just for arriving first. | Os créditos ficam estáveis até a zona ter três exploradores, para ninguém ganhar mais só por chegar primeiro. | Credits explainer |

## 6. Creating a pin

| Key | English | Português | Where |
| --- | --- | --- | --- |
| `pin.add` | Add a pin | Adicionar pino | Floating button |
| `pin.photo_title` | Photograph what you see | Fotografa o que vês | Camera screen |
| `pin.category_title` | What is it? | O que é? | Category step |
| `pin.cat_fix` | Needs fixing | Precisa de reparação | Chip |
| `pin.cat_protect` | Needs protecting | Precisa de proteção | Chip |
| `pin.cat_help` | Needs help | Precisa de ajuda | Chip |
| `pin.note` | Add a note (optional) | Adicionar nota (opcional) | Disclosure |
| `pin.note_placeholder` | One line: what is wrong? | Uma linha: o que está mal? | Text field |
| `pin.location_title` | Is the pin in the right place? | O pino está no sítio certo? | Location step |
| `pin.use_my_position` | Use my position | Usar a minha posição | Button |
| `pin.move` | Move the pin | Mover o pino | Button |
| `pin.publish` | Send | Enviar | Primary button |
| `pin.private_warning` | Only pin public places. Never enter private property or a road to reach a pin. | Marca apenas locais públicos. Nunca entres em propriedade privada nem numa estrada para chegar a um pino. | Safety line |
| `pin.uploading` | Sending your pin… | A enviar o teu pino… | Upload state |
| `pin.saved_offline` | Saved on this phone. It will send when you are online. | Guardado neste telemóvel. Envia quando tiveres ligação. | Offline |

## 7. Duplicates

| Key | English | Português | Where |
| --- | --- | --- | --- |
| `dup.title` | Someone already reported this | Alguém já reportou isto | Confirm step |
| `dup.body` | It is {metres} m away and was reported {when}. Confirm it instead? | Está a {metres} m e foi reportado {when}. Queres confirmar em vez disso? | Same step |
| `dup.confirm` | Confirm it | Confirmar | Primary button |
| `dup.create_anyway` | Mine is different | O meu é diferente | Secondary button |
| `dup.merged` | Merged. Both photos are kept and both of you get credit. | Unido. As duas fotos ficam guardadas e ambos recebem crédito. | After moderation |

## 8. Confirmation

| Key | English | Português | Where |
| --- | --- | --- | --- |
| `confirm.title` | Is it still like this? | Continua assim? | Pin sheet |
| `confirm.primary` | I can see it | Estou a ver | Primary button |
| `confirm.gone` | It's gone | Já não está | Secondary |
| `confirm.unsure` | Not sure | Não sei | Secondary |
| `confirm.too_far` | You are {metres} m away. Confirm within {radius} m. | Estás a {metres} m. Confirma a menos de {radius} m. | Error |
| `confirm.done` | Confirmed. This pin now counts for the street. | Confirmado. Este pino conta agora para a rua. | Result toast |
| `confirm.already` | You already confirmed this pin. | Já confirmaste este pino. | Error |
| `confirm.still_there` | Reported 14 days ago. Is it still there? | Reportado há 14 dias. Continua lá? | Age prompt |

## 9. Status timeline

| Key | English | Português | Where |
| --- | --- | --- | --- |
| `status.reported` | Reported | Reportado | Timeline |
| `status.confirmed` | Confirmed by a neighbour | Confirmado por um vizinho | Timeline |
| `status.fixed` | Fixed | Resolvido | Timeline |
| `status.after_photo` | Add a photo of the result | Adicionar foto do resultado | Fixed action |
| `status.next_reported` | Waiting for a second scout | À espera de um segundo explorador | Next step |
| `status.next_confirmed` | Waiting for a fix | À espera de resolução | Next step |
| `status.next_fixed` | Done. Thank you. | Concluído. Obrigado. | Next step |

## 10. Empty map

| Key | English | Português | Where |
| --- | --- | --- | --- |
| `empty.city_title` | No pins here yet | Ainda não há pinos aqui | Empty city |
| `empty.city_body` | Be the first scout. Five pins on your usual walk are enough to start. | Sê o primeiro explorador. Cinco pinos no teu caminho habitual chegam para começar. | Same screen |
| `empty.street_cta` | Adopt this street for a week | Adotar esta rua por uma semana | Zero-pin street |
| `empty.street_body` | Five pins, one street, seven days. We will show your progress here. | Cinco pinos, uma rua, sete dias. Mostramos o teu progresso aqui. | Same screen |
| `empty.seeded` | Added by the Civic Perks team | Adicionado pela equipa Civic Perks | Seeded pin label |

## 11. Reports and safety

| Key | English | Português | Where |
| --- | --- | --- | --- |
| `report.action` | Report | Denunciar | Pin/user menu |
| `report.title` | What is wrong? | O que está mal? | Report sheet |
| `report.false` | Not true | Não é verdade | Reason |
| `report.duplicate` | Duplicate | Duplicado | Reason |
| `report.unsafe` | Unsafe place | Local inseguro | Reason |
| `report.private` | Private property | Propriedade privada | Reason |
| `report.offensive` | Offensive | Ofensivo | Reason |
| `report.sent` | Sent to a person for review. We aim to answer within 48 hours. | Enviado para revisão humana. Respondemos em até 48 horas. | Confirmation |
| `block.action` | Block this scout | Bloquear este explorador | User menu |
| `block.done` | Their pins are hidden for you. | Os pinos desta pessoa ficam escondidos para ti. | Confirmation |
| `safety.title` | Look after yourself | Cuida de ti | First-pin interstitial |
| `safety.body` | Only visit public places. Do not use the app while driving or crossing a road. This is not an emergency service. | Visita apenas locais públicos. Não uses a aplicação a conduzir nem a atravessar a estrada. Isto não é um serviço de emergência. | Same |

## 12. Notifications

| Key | English | Português | Where |
| --- | --- | --- | --- |
| `notify.permission` | Tell me when a neighbour confirms my pins? | Avisar quando um vizinho confirmar os meus pinos? | After first confirmation |
| `notify.confirmed_title` | Your pin was confirmed | O teu pino foi confirmado | Push |
| `notify.confirmed_body` | {category} on {street}. It now counts for the street. | {category} na {street}. Conta agora para a rua. | Push |
| `notify.report_ready` | Your weekly report is ready | O teu relatório semanal está pronto | Push/email |
| `notify.quiet` | Quiet hours: 22:00–08:00 | Horas de silêncio: 22:00–08:00 | Settings |

## 13. Errors worth rewriting

| Key | Instead of | English |
| --- | --- | --- |
| `error.upload` | "Upload failed" | "The photo did not send. It is saved on this phone — try again." |
| `error.location` | "Permission denied" | "We cannot read your position. You can still place the pin by tapping the map." |
| `error.network` | "Network error" | "No connection. Your pin is waiting on this phone." |
| `error.too_far` | "Out of range" | "You are {metres} m away. Confirmation works within {radius} m." |
| `error.duplicate` | "Duplicate pin" | "This looks like the pin {metres} m away. Confirm that one instead?" |
| `error.session` | "Auth error" | "Your session ended. Sign in again — your drafts are safe." |

## 14. Copy rules to keep

- One idea per sentence; one action per button.
- Numbers carry units and local time; never "soon" or "shortly".
- "Scout" for a person, "pin" for the report, "street" for the place, "credits" for the
  economy. Never mix with "user", "marker", "zone" in user-facing strings.
- Say what still works before what is blocked.
- No promises about safety, accuracy or response time that the app cannot keep.
- Do not use "free" for anything that costs attention or an ad.
