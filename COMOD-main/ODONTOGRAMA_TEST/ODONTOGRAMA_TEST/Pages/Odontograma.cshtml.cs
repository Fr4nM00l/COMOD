namespace ODONTOGRAMA_TEST.Pages
{
    using Microsoft.AspNetCore.Mvc;
    using Microsoft.AspNetCore.Mvc.RazorPages;
    using MySql.Data.MySqlClient;
    using ODONTOGRAMA_TEST.Pages.Clases;

    public class OdontogramaModel : PageModel
    {
        [BindProperty]
        public string DNI { get; set; }

        public Odontograma Odontograma { get; set; }

        public string NombrePaciente { get; set; }

        public string ErrorMensaje { get; set; }

        public void OnPost()
        {
            if (string.IsNullOrWhiteSpace(DNI))
            {
                ErrorMensaje = "Por favor ingrese un DNI.";
                return;
            }

            string connectionString = "server=localhost;database=clinicaodontologica;user=root;password=;";
            using var conn = new MySqlConnection(connectionString);
            conn.Open();

            // Obtener nombre del paciente
            string nombreQuery = "SELECT Nombre FROM paciente WHERE DNI = @dni";
            using (var cmdNombre = new MySqlCommand(nombreQuery, conn))
            {
                cmdNombre.Parameters.AddWithValue("@dni", DNI);
                var result = cmdNombre.ExecuteScalar();
                if (result == null)
                {
                    ErrorMensaje = "No se encontró un paciente con ese DNI.";
                    return;
                }
                NombrePaciente = result.ToString();
            }

            // Obtener odontograma completo
            string query = @"
            SELECT 
                o.id AS OdontogramaId,
                o.Fecha AS FechaOdontograma,
                dd.NumDiente,
                a.NombreAfeccion,
                da.ZonaDiente
            FROM paciente p
            JOIN historiaclinica hc ON hc.Paciente_id = p.id
            JOIN odontograma o ON o.HistoriaClinica_id = hc.id
            JOIN detallediente dd ON dd.Odontograma_id = o.id
            LEFT JOIN detalleafeccion da ON da.DetalleDiente_id = dd.id
            LEFT JOIN afeccion a ON a.id = da.Afeccion_id
            WHERE p.DNI = @dni
            ORDER BY o.Fecha DESC, dd.NumDiente;";

            using var cmd = new MySqlCommand(query, conn);
            cmd.Parameters.AddWithValue("@dni", DNI);

            using var reader = cmd.ExecuteReader();

            var dientesDict = new Dictionary<int, Diente>();
            Odontograma = new Odontograma();

            while (reader.Read())
            {
                if (Odontograma.Id == 0)
                {
                    Odontograma.Id = reader.GetInt32("OdontogramaId");
                    Odontograma.Fecha = reader.GetDateTime("FechaOdontograma");
                }

                int numDiente = reader.GetInt32("NumDiente");
                if (!dientesDict.ContainsKey(numDiente))
                    dientesDict[numDiente] = new Diente { Numero = numDiente };

                if (!reader.IsDBNull(reader.GetOrdinal("NombreAfeccion")))
                {
                    dientesDict[numDiente].Afecciones.Add(new Afeccion
                    {
                        Nombre = reader.GetString("NombreAfeccion"),
                        ZonaDiente = reader.GetString("ZonaDiente")
                    });
                }
            }

            Odontograma.Dientes = dientesDict.Values.ToList();
        }
    }


}
