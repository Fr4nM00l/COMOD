namespace ODONTOGRAMA_TEST.Pages.Clases
{
    public class Paciente
    {
        public string Nombre { get; set; }
        public string DNI { get; set; }
    }

    public class Afeccion
    {
        public string Nombre { get; set; }
        public string ZonaDiente { get; set; }
    }

    public class Diente
    {
        public int Numero { get; set; }
        public List<Afeccion> Afecciones { get; set; } = new List<Afeccion>();
    }

    public class Odontograma
    {
        public int Id { get; set; }
        public DateTime Fecha { get; set; }
        public List<Diente> Dientes { get; set; } = new List<Diente>();
    }

}
