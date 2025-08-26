<?php
require_once "myAPI/src/http/Response.php";
require_once "myAPI/src/utils/Logger.php";
class Database
{
  /** @var string Endereço do servidor de banco de dados (IP local) */
  private const HOST = '127.0.0.1';

  /** @var string Nome de usuário com privilégios no banco de dados */
  private const USER = 'root';

  /** @var string Senha de acesso ao banco de dados (vazia por padrão em desenvolvimento) */
  private const PASSWORD = '';

  /** @var string Nome do banco de dados que será utilizado */
  private const DATABASE = 'BancoDoHelio';

  /** @var int Porta padrão do MySQL/MariaDB */
  private const PORT = 3306;

  /** @var string Charset que suporta todos os caracteres Unicode (incluindo emojis) */
  private const CHARACTER_SET = 'utf8mb4';

  /** 
   * @var PDO|null Instância única da conexão PDO (implementação do Singleton) 
   * @static A propriedade é estática para ser compartilhada por todas as instâncias da classe
   */
  private static ?PDO $CONNECTION = null;


  /**
   * Obtém a instância ativa da conexão PDO com o banco de dados.
   * 
   * Este método implementa o padrão Singleton para garantir que apenas uma única conexão
   * seja utilizada durante o ciclo de vida da aplicação. Se a conexão não existir (null),
   * o método automaticamente chama Database::connect() para estabelecer uma nova conexão.
   *
   * O método pode retornar null apenas no tipo de retorno para compatibilidade, mas na prática,
   * quando chamado, sempre retornará um objeto PDO válido (ou lançará uma exceção em caso de falha).
   *
   * @return PDO|null Retorna a instância ativa de PDO ou null se a conexão não puder ser estabelecida
   *                  (embora na prática, quando chamado, sempre retorne PDO devido ao connect() interno)
   * @throws PDOException Se uma nova conexão for necessária e falhar ao ser estabelecida
   *                      (propagada do método connect())
   *
   * @uses Database::$CONNECTION Armazenamento estático da conexão PDO
   * @uses Database::connect() Método para estabelecer nova conexão quando necessário
   *
   * @example
   * // Uso típico (a conexão será criada na primeira chamada)
   * $pdo = Database::getConnection();
   * 
   * try {
   *     $stmt = $pdo->query("SELECT * FROM products");
   *     foreach ($stmt as $product) {
   *         echo $product->name;
   *     }
   * } catch (PDOException $e) {
   *     // Tratar erros de banco de dados
   * }
   *
   * @see Database::connect() Para detalhes sobre como a conexão é estabelecida
   */
  public static function getConnection(): PDO|null
  {
    // Verifica se a conexão já existe
    if (Database::$CONNECTION === null) {
      // Se não existir, estabelece uma nova conexão
      Database::connect();
    }

    // Retorna a conexão existente ou recém-criada
    return Database::$CONNECTION;
  }

  /**
   * Estabelece uma conexão com o banco de dados usando PDO (PHP Data Objects).
   * 
   * Este método privado e estático cria uma conexão singleton com o banco de dados MySQL/MariaDB
   * utilizando as constantes definidas na classe Database. A conexão é armazenada estaticamente
   * para reutilização e retornada para o chamador.
   *
   * A conexão é configurada com os seguintes atributos importantes:
   * - Define o modo de erro para lançar exceções (PDO::ERRMODE_EXCEPTION)
   * - Configura o fetch padrão para retornar objetos anônimos (PDO::FETCH_OBJ)
   *
   * @return PDO Retorna uma instância de PDO representando a conexão com o banco de dados
   * @throws PDOException Se a conexão com o banco de dados falhar
   *
   * @uses Database::HOST Endereço do servidor de banco de dados
   * @uses Database::PORT Porta de conexão do banco de dados
   * @uses Database::DATABASE Nome do banco de dados
   * @uses Database::CHARACTER_SET Charset utilizado na comunicação
   * @uses Database::USER Nome de usuário para autenticação
   * @uses Database::PASSWORD Senha para autenticação
   * @uses Database::$CONNECTION Armazena a conexão para reutilização
   *
   * @example
   * try {
   *     $pdo = Database::connect();
   *     $stmt = $pdo->query("SELECT * FROM users");
   *     foreach ($stmt as $user) {
   *         echo $user->name;
   *     }
   * } catch (PDOException $e) {
   *     // Tratar erro de conexão
   * }
   */
  private static function connect(): PDO
  {
    // Formata a string DSN (Data Source Name) com os parâmetros de conexão
    $dsn = sprintf(
      'mysql:host=%s;port=%d;dbname=%s;charset=%s',
      Database::HOST,
      Database::PORT,
      Database::DATABASE,
      Database::CHARACTER_SET
    );

    // Cria a instância PDO com os parâmetros de conexão
    Database::$CONNECTION = new PDO(
      dsn: $dsn,                          // String de conexão formatada
      username: Database::USER,           // Usuário do banco de dados
      password: Database::PASSWORD,       // Senha do banco de dados
      options: [                          // Opções de configuração
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, // Lança exceções em erros
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_OBJ // Retorna objetos por padrão
      ]
    );

    return Database::$CONNECTION;
  }

  /**
   * Realiza o backup completo do banco de dados atual para um arquivo SQL.
   * 
   * Este método estático executa um dump completo de todas as tabelas do banco de dados
   * configurado na classe Database, gerando um arquivo .sql no diretório especificado.
   * 
   * Funcionamento detalhado:
   * 1. Gera um nome de arquivo com timestamp no formato 'backup_YYYY_mm_dd_HH_ii_ss.sql'
   * 2. Cria o diretório de backup se não existir (com permissões 0777)
   * 3. Lista todas as tabelas do banco de dados atual
   * 4. Gera o arquivo de backup com a estrutura e dados de cada tabela
   * 
   * Tratamento de erros:
   * - Se falhar ao criar o arquivo, registra o erro no Logger
   * - Envia uma resposta HTTP 500 em caso de falha
   * 
   * Segurança:
   * - O diretório é criado com permissões amplas (0777) para garantir funcionamento
   * - Em produção, considere restringir permissões após a criação
   * 
   * @return void
   * @throws PDOException Se ocorrer erro ao acessar o banco de dados
   * 
   * @uses Database::getConnection() Para obter a conexão PDO ativa
   * @uses Logger::log() Para registrar erros durante o processo
   * @uses Response Para enviar respostas HTTP em caso de falha
   * 
   * @example
   * // Execução simples
   * Database::backup();
   * 
   * // Em um contexto de controller
   * try {
   *     Database::backup();
   *     echo "Backup realizado com sucesso!";
   * } catch (Exception $e) {
   *     echo "Erro ao realizar backup: " . $e->getMessage();
   * }
   */
  public static function backup(): void
  {
    // Caminho relativo do arquivo de backup
    $backupPath = "system/backup_" . date('Y_m_d_H_i_s') . ".sql";

    // Garante que o diretório exista
    $directory = dirname($backupPath);
    if (!is_dir($directory)) {
      mkdir($directory, 0777, true); // Cria o diretório e os pais, se necessário
    }

    $pdo = self::getConnection();
    $tables = $pdo->query("SHOW TABLES")->fetchAll(PDO::FETCH_COLUMN);

    $backupFile = fopen($backupPath, 'w');

    if ($backupFile === false) {
      Logger::log(new \Exception('Erro ao criar o arquivo de backup.'));
      (new Response(
        success: false,
        message: 'Erro ao criar o arquivo de backup.',
        httpCode: 500
      ))->send();
      return;
    }

    foreach ($tables as $table) {
      // Escrever estrutura da tabela
      $createTableStmt = $pdo->query("SHOW CREATE TABLE `$table`")->fetch(PDO::FETCH_ASSOC);
      fwrite($backupFile, $createTableStmt['Create Table'] . ";\n\n");

      // Contar total de registros da tabela
      $total = $pdo->query("SELECT COUNT(*) FROM `$table`")->fetchColumn();
      $limit = 1000;

      for ($offset = 0; $offset < $total; $offset += $limit) {
        $stmt = $pdo->prepare("SELECT * FROM `$table` LIMIT :limit OFFSET :offset");
        $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
        $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
        $stmt->execute();

        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

        foreach ($rows as $row) {
          $columns = array_keys($row);
          $values = array_map([$pdo, 'quote'], array_values($row)); // forma segura

          $insertStmt = sprintf(
            "INSERT INTO `%s` (`%s`) VALUES (%s);\n",
            $table,
            implode('`, `', $columns),
            implode(', ', $values)
          );
          fwrite($backupFile, $insertStmt);
        }
      }

      fwrite($backupFile, "\n\n"); // Separação entre tabelas
    }

    fclose($backupFile);

    // Envia o arquivo para download
    header('Content-Description: File Transfer');
    header('Content-Type: application/sql');
    header('Content-Disposition: attachment; filename="' . basename($backupPath) . '"');
    header('Content-Length: ' . filesize($backupPath));
    header('Pragma: no-cache');
    header('Expires: 0');
    readfile($backupPath);

    //unlink($backupPath); // Opcional: remover após envio
    exit;
  }


}