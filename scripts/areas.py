"""Classificação de projetos em áreas temáticas, por palavras da ementa."""
import re, unicodedata

def norm(s):
    return unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode()

AREAS = [
("Tributário e fiscal", r"tribut|imposto|icms|ipva|itcd|fiscal|isencao|receita estadual|contribuinte|divida ativa|credito presumido|substituicao tributaria|beneficio fiscal|\bsonegac"),
("Ambiental", r"ambient|sustentab|clima|residuo|reciclag|poluic|licenciamento|\bfauna|\bflora|biodivers|reflorest|desmatament|queimada|agrotoxic|plastico|unidade de conservacao|ecolog|carbono|catastrofe|enchente|desastre|defesa civil"),
("Água e saneamento", r"\bagu(a|as)\b|saneamento|esgoto|hidric|bacia hidrografica|irrigacao|corsan"),
("Energia", r"energia|eletric|\bsolar\b|eolic|\bceee\b|\brge\b|aneel|combustiv|gas natural|gasolina|etanol|biodiesel|hidrogenio|bioenergia|iluminacao"),
("Direitos humanos e minorias", r"direitos humanos|racial|racismo|quilombol|indigena|lgbt|igualdade|discrimin|xenofob|intolerancia|etnic|populacao negra|refugiad|trafico de pessoas|liberdade religiosa|\bcidadania\b|vulnerabilidade"),
("Mulher e combate à violência", r"mulher|mulheres|feminic|maria da penha|violencia domestica|gestante|medida protetiva|misoginia"),
("Infância e juventude", r"crianca|adolescent|infanto|juventude|\bjovens?\b|estatuto da crianca|conselho tutelar|primeira infancia|apadrinhamento|\bescolar"),
("Pessoa idosa e com deficiência", r"\bidos[oa]s?\b|terceira idade|envelhec|deficien|\bpcds?\b|autis|\btea\b|espectro autista|neurodiverg|acessibilidad|cadeirante|\blibras\b|\bsurd|\bcego|\braras?\b|\bdown\b"),
("Saúde", r"saude|hospital|\bsus\b|medic|vacina|doenc|cancer|oncolog|mental|farmac|enferm|ambulatori|\bsamu\b|\bexames?\b|paciente|cirurg|transplant|\bubs\b|\bleitos?\b|dependencia quimica|dependentes quimic|medicament|\bsangue|\bdoador"),
("Educação", r"educac|escola|ensino|estudant|professor|universit|alfabetiz|creche|uergs|vestibular|\balunos?\b|bullying|merenda|curricul|docente"),
("Segurança pública", r"seguranca publica|policia|policial|penitenci|presidi|\bcrimes?\b|criminal|\barmas?\b|bombeiro|delegacia|brigada|susepe|apenad|\bpresos?\b|encarcer|videomonitor|\bfurto|\broubo|trafico de drogas|pirataria|facc"),
("Transportes e rodovias", r"rodovia|transporte|transito|pedagio|ferrovi|mobilidade|aeroporto|veicul|motorist|detran|\bdaer\b|onibus|estrada|\bcnh\b|habilitacao|aeroviari|ciclovia|motocicl|\bmotos?\b|\btrens?\b"),
("Agropecuária e rural", r"agricol|rural|agropecuar|produtor|lavoura|\bleite|\barroz|safra|cooperativ|pecuaria|suino|\baves\b|\bpesca\b|aquicultur|fumicultur|apicultur|emater|defesa sanitaria|rebanho|agroindustr|\bvinho|vitivinicol|erva-mate|agricultura familiar|estiagem"),
("Economia, trabalho e empresas", r"empresa|microempre|empreend|trabalh|emprego|econom|comercio|industri|\bcredito|investiment|startup|salari|piso|banrisul|badesul|cadeia produtiva|\bmei\b|franquia"),
("Servidores e previdência", r"servidor|funcionalismo|aposentad|previd|pensao|pensionist|remuneracao|reajuste|carreira|concurso|\bcargos?\b|\bipe\b|rsprev|militar estadual|quadro de pessoal|ipergs|subsidio"),
("Administração e orçamento", r"orcamento|\bldo\b|\bloa\b|lei orcamentaria|\bppa\b|credito suplementar|credito adicional|estima a receita|fixa a despesa|transparencia|licitacao|contrato|convenio|gestao publica|controle interno|tribunal de contas|defensoria|ministerio publico|poder judiciario|poder executivo|estrutura organizacional|reestrutur|autarquia|fundacao|operacao de credito|divida publica|regime de recuperacao"),
("Habitação e urbanismo", r"habitac|moradia|urban|regularizacao fundiaria|loteamento|emancipac|condominio|imovel|plano diretor|aluguel|reurb|metropolitan"),
("Consumidor e serviços", r"consumidor|procon|tarifa|telefon|internet|\bbancos?\b|plano de saude|operadora|prestador|servicos? publicos?|concession|fatura|cobranca|propaganda|publicidade|\bseguros?\b|propriedade intelectual"),
("Cultura, esporte e turismo", r"cultur|esport|turism|\bevento|festival|patrimonio|musica|tradicion|artist|museu|biblioteca|cinema|teatro|futebol|atleta|folclor|\bgaucho|\bfeira|exposicao|\blazer\b|desporto"),
("Ciência, tecnologia e inovação", r"tecnolog|inteligencia artificial|\bdigital|ciencia|pesquisa|data center|inovac|cibernet|dados pessoais|\blgpd\b|software|tecnopole|parque tecnologico|\bdrones?\b"),
("Proteção animal", r"\banimal|\banimais|\bpets?\b|\bcaes\b|\bcachorro|\bgatos?\b|maus-tratos|zoonose|castracao|\btutor|silvestre|canil"),
("Homenagens e datas", r"relevante interesse|utilidade publica|denomina|institui o dia|institui a semana|institui o mes|capital estadual|homenag|titulo de|dia estadual|semana estadual|calendario oficial|\bfestas?\b|datas comemorativas"),
("Assuntos registrais", r"registro de imove|registro imobiliari|cartorio|\bcartorari|\bnotari|tabelia|tabelionato|serventia|\bescritura|registro civil|registro de titulos|registro de pessoas|registro publico|registro de nascimento|registro de obito|registro de casamento|certidao de (nascimento|obito|casamento|inteiro teor)|certidoes de (nascimento|obito|casamento)|usucapia|averbac|oficial de registro|registrador|\bregistrais?\b|\bregistral|\bemolumento|protesto de titulo|\bcnj\b|regularizacao fundiaria|\breurb\b|\bfe publica|notas e registro|\buniao estavel|\buni(o|oe)es estaveis"),
]
_COMP = [(a, re.compile(r)) for a, r in AREAS]

def classificar(ementa):
    t = norm(ementa or '')
    return [a for a, r in _COMP if r.search(t)]
